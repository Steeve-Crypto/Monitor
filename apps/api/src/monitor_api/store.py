from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from threading import RLock
from typing import Protocol

from monitor_api.models import Opportunity, ProjectSignal

DEFAULT_STORAGE_PATH = Path(".monitor") / "signal_mesh_store.json"
STORAGE_PATH_ENV = "MONITOR_SIGNAL_MESH_STORE_PATH"


class SignalMeshStore(Protocol):
    def list_signals(self) -> list[ProjectSignal]: ...

    def get_signal(self, signal_id: str) -> ProjectSignal | None: ...

    def add_signal(self, signal: ProjectSignal) -> ProjectSignal: ...

    def add_signals(self, signals: list[ProjectSignal]) -> list[ProjectSignal]: ...

    def list_opportunities(self) -> list[Opportunity]: ...

    def get_opportunity_by_source_signal_id(self, signal_id: str) -> Opportunity | None: ...

    def add_opportunity(self, opportunity: Opportunity) -> Opportunity: ...

    def update_signal(self, signal: ProjectSignal) -> ProjectSignal: ...

    def stats(self) -> dict[str, object]: ...


class JsonSignalMeshStore:
    def __init__(self, storage_path: str | Path | None = None) -> None:
        self.storage_path = (
            Path(storage_path) if storage_path is not None else default_storage_path()
        )
        self._lock = RLock()
        self._signals: list[ProjectSignal] = []
        self._opportunities: list[Opportunity] = []
        self._load()

    def list_signals(self) -> list[ProjectSignal]:
        with self._lock:
            return list(self._signals)

    def get_signal(self, signal_id: str) -> ProjectSignal | None:
        with self._lock:
            return next((signal for signal in self._signals if signal.id == signal_id), None)

    def add_signal(self, signal: ProjectSignal) -> ProjectSignal:
        with self._lock:
            if self._has_signal(signal):
                return signal
            self._signals.append(signal)
            self._save()
        return signal

    def add_signals(self, signals: list[ProjectSignal]) -> list[ProjectSignal]:
        with self._lock:
            new_signals: list[ProjectSignal] = []
            seen_keys = {signal_identity_key(signal) for signal in self._signals}
            for signal in signals:
                key = signal_identity_key(signal)
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                new_signals.append(signal)
            if new_signals:
                self._signals.extend(new_signals)
                self._save()
        return new_signals

    def list_opportunities(self) -> list[Opportunity]:
        with self._lock:
            return list(self._opportunities)

    def get_opportunity_by_source_signal_id(self, signal_id: str) -> Opportunity | None:
        with self._lock:
            return next(
                (
                    opportunity
                    for opportunity in self._opportunities
                    if opportunity.source_signal_id == signal_id
                ),
                None,
            )

    def add_opportunity(self, opportunity: Opportunity) -> Opportunity:
        with self._lock:
            self._opportunities.append(opportunity)
            self._save()
        return opportunity

    def update_signal(self, signal: ProjectSignal) -> ProjectSignal:
        with self._lock:
            for index, existing in enumerate(self._signals):
                if existing.id == signal.id:
                    self._signals[index] = signal
                    self._save()
                    return signal
        return signal

    def stats(self) -> dict[str, object]:
        with self._lock:
            return {
                "signals_count": len(self._signals),
                "opportunities_count": len(self._opportunities),
                "storage_path": str(self.storage_path),
                "storage_exists": self.storage_path.exists(),
            }

    def _load(self) -> None:
        with self._lock:
            if not self.storage_path.exists():
                self._signals = []
                self._opportunities = []
                return

            raw = json.loads(self.storage_path.read_text(encoding="utf-8"))
            self._signals = [ProjectSignal.model_validate(item) for item in raw.get("signals", [])]
            self._opportunities = [
                Opportunity.model_validate(item) for item in raw.get("opportunities", [])
            ]

    def _save(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "signals": [
                signal.model_dump(mode="json") for signal in self._signals
            ],
            "opportunities": [
                opportunity.model_dump(mode="json") for opportunity in self._opportunities
            ],
        }
        serialized = json.dumps(payload, indent=2, sort_keys=True)

        fd, temp_name = tempfile.mkstemp(
            prefix=f".{self.storage_path.name}.",
            suffix=".tmp",
            dir=self.storage_path.parent,
            text=True,
        )
        temp_path = Path(temp_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as temp_file:
                temp_file.write(serialized)
                temp_file.write("\n")
            temp_path.replace(self.storage_path)
        except Exception:
            temp_path.unlink(missing_ok=True)
            raise

    def _has_signal(self, signal: ProjectSignal) -> bool:
        key = signal_identity_key(signal)
        return any(signal_identity_key(existing) == key for existing in self._signals)


def default_storage_path() -> Path:
    configured = os.getenv(STORAGE_PATH_ENV)
    if configured:
        return Path(configured)
    return DEFAULT_STORAGE_PATH


def signal_identity_key(signal: ProjectSignal) -> tuple[str, str]:
    return (signal.source_platform.value, signal.source_id)
