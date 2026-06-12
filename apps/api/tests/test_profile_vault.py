import json

from fastapi.testclient import TestClient

from monitor_api.app import create_app


def test_profile_vault_stores_profiles_encrypted_at_rest(tmp_path):
    vault_path = tmp_path / "profiles.vault"
    client = TestClient(
        create_app(storage_path=tmp_path / "signal_mesh.json", vault_path=vault_path)
    )
    headers = {"X-Vault-Password": "correct horse battery staple"}

    response = client.post(
        "/api/profiles",
        headers=headers,
        json={
            "display_name": "Local Builder",
            "target_roles": ["backend engineer"],
            "target_skills": ["python", "fastapi", "web3"],
            "preferred_platforms": ["upwork", "discord"],
            "max_daily_autopilot_sends": 0,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"].startswith("prof_")
    assert body["display_name"] == "Local Builder"
    assert vault_path.exists()
    raw_vault = vault_path.read_text(encoding="utf-8")
    assert "Local Builder" not in raw_vault
    assert "fastapi" not in raw_vault
    assert "correct horse battery staple" not in raw_vault

    list_response = client.get("/api/profiles", headers=headers)
    assert list_response.status_code == 200
    assert list_response.json()["count"] == 1
    assert list_response.json()["items"][0]["display_name"] == "Local Builder"


def test_profile_vault_rejects_missing_or_wrong_password(tmp_path):
    vault_path = tmp_path / "profiles.vault"
    client = TestClient(
        create_app(storage_path=tmp_path / "signal_mesh.json", vault_path=vault_path)
    )
    headers = {"X-Vault-Password": "vault-password"}
    create_response = client.post(
        "/api/profiles",
        headers=headers,
        json={"display_name": "Private Profile"},
    )
    assert create_response.status_code == 201

    missing_response = client.get("/api/profiles")
    wrong_response = client.get("/api/profiles", headers={"X-Vault-Password": "wrong-password"})

    assert missing_response.status_code == 401
    assert wrong_response.status_code == 403


def test_profile_vault_persists_profiles_across_app_instances(tmp_path):
    vault_path = tmp_path / "profiles.vault"
    headers = {"X-Vault-Password": "vault-password"}
    first_client = TestClient(
        create_app(storage_path=tmp_path / "signal_mesh.json", vault_path=vault_path)
    )
    created = first_client.post(
        "/api/profiles",
        headers=headers,
        json={"display_name": "Persistent Profile", "target_skills": ["python"]},
    )
    assert created.status_code == 201

    second_client = TestClient(
        create_app(storage_path=tmp_path / "signal_mesh.json", vault_path=vault_path)
    )
    list_response = second_client.get("/api/profiles", headers=headers)

    assert list_response.status_code == 200
    assert list_response.json()["items"][0]["id"] == created.json()["id"]
    # The vault file should be an envelope, not plaintext JSON profile storage.
    vault_envelope = json.loads(vault_path.read_text(encoding="utf-8"))
    assert set(vault_envelope) == {"version", "kdf", "salt", "token"}
