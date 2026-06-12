from __future__ import annotations

import base64
import json
import os
import tempfile
from pathlib import Path
from threading import RLock

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pydantic import ValidationError

from monitor_api.models import Profile

DEFAULT_VAULT_PATH = Path(".monitor") / "profile_vault.json"
VAULT_PATH_ENV = "MONITOR_PROFILE_VAULT_PATH"
PBKDF2_ITERATIONS = 390_000


class VaultPasswordError(ValueError):
    pass


class ProfileVault:
    def __init__(self, vault_path: str | Path | None = None) -> None:
        self.vault_path = Path(vault_path) if vault_path is not None else default_vault_path()
        self._lock = RLock()

    def list_profiles(self, password: str) -> list[Profile]:
        self._require_password(password)
        with self._lock:
            if not self.vault_path.exists():
                return []
            return self._load_profiles(password)

    def add_profile(self, profile: Profile, password: str) -> Profile:
        self._require_password(password)
        with self._lock:
            profiles = self._load_profiles(password) if self.vault_path.exists() else []
            profiles.append(profile)
            self._save_profiles(profiles, password)
        return profile

    def get_profile(self, profile_id: str, password: str) -> Profile | None:
        for profile in self.list_profiles(password):
            if profile.id == profile_id:
                return profile
        return None

    def _load_profiles(self, password: str) -> list[Profile]:
        envelope = json.loads(self.vault_path.read_text(encoding="utf-8"))
        try:
            salt = base64.urlsafe_b64decode(envelope["salt"].encode("ascii"))
            token = envelope["token"].encode("ascii")
        except (KeyError, ValueError) as exc:
            raise VaultPasswordError("Invalid profile vault envelope.") from exc

        fernet = Fernet(_derive_key(password, salt))
        try:
            raw_payload = fernet.decrypt(token)
        except InvalidToken as exc:
            raise VaultPasswordError("Profile vault password is invalid.") from exc

        try:
            payload = json.loads(raw_payload.decode("utf-8"))
            return [Profile.model_validate(item) for item in payload.get("profiles", [])]
        except (json.JSONDecodeError, ValidationError) as exc:
            raise VaultPasswordError("Profile vault payload is invalid.") from exc

    def _save_profiles(self, profiles: list[Profile], password: str) -> None:
        salt = os.urandom(16)
        fernet = Fernet(_derive_key(password, salt))
        payload = {
            "profiles": [profile.model_dump(mode="json") for profile in profiles],
        }
        token = fernet.encrypt(json.dumps(payload, sort_keys=True).encode("utf-8"))
        envelope = {
            "version": 1,
            "kdf": f"PBKDF2HMAC-SHA256:{PBKDF2_ITERATIONS}",
            "salt": base64.urlsafe_b64encode(salt).decode("ascii"),
            "token": token.decode("ascii"),
        }
        self._write_atomic(json.dumps(envelope, indent=2, sort_keys=True))

    def _write_atomic(self, serialized: str) -> None:
        self.vault_path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(
            prefix=f".{self.vault_path.name}.",
            suffix=".tmp",
            dir=self.vault_path.parent,
            text=True,
        )
        temp_path = Path(temp_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as temp_file:
                temp_file.write(serialized)
                temp_file.write("\n")
            temp_path.replace(self.vault_path)
        except Exception:
            temp_path.unlink(missing_ok=True)
            raise

    def _require_password(self, password: str) -> None:
        if not password:
            raise VaultPasswordError("Profile vault password is required.")


def default_vault_path() -> Path:
    configured = os.getenv(VAULT_PATH_ENV)
    if configured:
        return Path(configured)
    return DEFAULT_VAULT_PATH


def _derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))
