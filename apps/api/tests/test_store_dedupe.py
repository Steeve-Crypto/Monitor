from monitor_api.models import Platform, ProjectSignal
from monitor_api.store import JsonSignalMeshStore


def test_json_store_deduplicates_signals_by_platform_and_source_id(tmp_path):
    store = JsonSignalMeshStore(tmp_path / "signal_mesh.json")
    first = ProjectSignal(
        source_platform=Platform.RSS,
        source_id="job-123",
        title="Python protocol engineer",
        raw_text="Need a Python engineer for web3 data tooling.",
    )
    duplicate = ProjectSignal(
        source_platform=Platform.RSS,
        source_id="job-123",
        title="Python protocol engineer duplicate",
        raw_text="Duplicate copy of the same job.",
    )

    stored = store.add_signals([first, duplicate])

    assert stored == [first]
    assert store.list_signals() == [first]
    assert JsonSignalMeshStore(tmp_path / "signal_mesh.json").list_signals()[0].title == first.title
