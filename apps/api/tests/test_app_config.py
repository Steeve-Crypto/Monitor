import pytest

from monitor_api.app import create_app
from monitor_api.store import JsonSignalMeshStore


def test_create_app_rejects_store_and_storage_path_together(tmp_path):
    store = JsonSignalMeshStore(tmp_path / "store.json")

    with pytest.raises(ValueError, match="Pass either store or storage_path"):
        create_app(store=store, storage_path=tmp_path / "other.json")
