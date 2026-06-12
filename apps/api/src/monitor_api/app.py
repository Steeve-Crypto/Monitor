from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from monitor_api import __version__
from monitor_api.models import Opportunity, ProjectSignal
from monitor_api.scanners import SignalMeshScanner, UnsupportedSignalSourceError
from monitor_api.store import JsonSignalMeshStore, SignalMeshStore


class HealthResponse(BaseModel):
    service: str
    status: str
    version: str


class ProjectSignalListResponse(BaseModel):
    items: list[ProjectSignal]
    count: int


class OpportunityListResponse(BaseModel):
    items: list[Opportunity]
    count: int


class ScanRequest(BaseModel):
    query: str
    limit: int = 10


class ScanResponse(BaseModel):
    source: str
    items: list[ProjectSignal]
    count: int


class StoreStatsResponse(BaseModel):
    signals_count: int
    opportunities_count: int
    storage_path: str
    storage_exists: bool


def create_app(
    store: SignalMeshStore | None = None,
    storage_path: str | Path | None = None,
    scanner: SignalMeshScanner | None = None,
) -> FastAPI:
    if store is not None and storage_path is not None:
        raise ValueError("Pass either store or storage_path, not both.")

    app = FastAPI(
        title="Monitor API",
        version=__version__,
        description=(
            "Local API for Monitor signal discovery, qualification, "
            "and risk/autopilot contracts."
        ),
    )
    signal_store = store if store is not None else JsonSignalMeshStore(storage_path)
    signal_scanner = scanner if scanner is not None else SignalMeshScanner.with_default_adapters()

    @app.get("/api/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(service="monitor-api", status="ok", version=__version__)

    @app.get("/api/signals", response_model=ProjectSignalListResponse)
    def list_signals() -> ProjectSignalListResponse:
        signals = signal_store.list_signals()
        return ProjectSignalListResponse(items=signals, count=len(signals))

    @app.post(
        "/api/signals",
        response_model=ProjectSignal,
        status_code=status.HTTP_201_CREATED,
    )
    def create_signal(signal: ProjectSignal) -> ProjectSignal:
        return signal_store.add_signal(signal)

    @app.post("/api/scans/{source}/run", response_model=ScanResponse)
    def run_scan(source: str, request: ScanRequest) -> ScanResponse:
        try:
            signals = signal_scanner.scan_source(source, query=request.query, limit=request.limit)
        except UnsupportedSignalSourceError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        new_signals = signal_store.add_signals(signals)
        return ScanResponse(source=source, items=new_signals, count=len(new_signals))

    @app.get("/api/store/stats", response_model=StoreStatsResponse)
    def store_stats() -> StoreStatsResponse:
        return StoreStatsResponse.model_validate(signal_store.stats())

    @app.get("/api/opportunities", response_model=OpportunityListResponse)
    def list_opportunities() -> OpportunityListResponse:
        opportunities = signal_store.list_opportunities()
        return OpportunityListResponse(items=opportunities, count=len(opportunities))

    @app.post(
        "/api/opportunities",
        response_model=Opportunity,
        status_code=status.HTTP_201_CREATED,
    )
    def create_opportunity(opportunity: Opportunity) -> Opportunity:
        return signal_store.add_opportunity(opportunity)

    return app


app = create_app()
