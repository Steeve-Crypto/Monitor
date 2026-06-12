from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Response, status
from pydantic import BaseModel

from monitor_api import __version__
from monitor_api.models import Opportunity, Profile, ProjectSignal
from monitor_api.profile_vault import ProfileVault, VaultPasswordError
from monitor_api.qualification import mark_signal_qualified, qualify_opportunity
from monitor_api.scanners import (
    SignalMeshScanner,
    SourceNotConfiguredError,
    UnsupportedSignalSourceError,
)
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


class ProfileListResponse(BaseModel):
    items: list[Profile]
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
    vault_path: str | Path | None = None,
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
    profile_vault = ProfileVault(vault_path)
    signal_scanner = scanner if scanner is not None else SignalMeshScanner.with_default_adapters()

    def require_vault_password(password: str | None) -> str:
        if not password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="X-Vault-Password header is required.",
            )
        return password

    def vault_error_to_http(exc: VaultPasswordError) -> HTTPException:
        detail = str(exc)
        if "required" in detail.lower():
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

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

    @app.post(
        "/api/signals/{signal_id}/qualify",
        response_model=Opportunity,
        status_code=status.HTTP_201_CREATED,
    )
    def qualify_signal(signal_id: str, response: Response) -> Opportunity:
        signal = signal_store.get_signal(signal_id)
        if signal is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Signal not found: {signal_id}",
            )

        existing = signal_store.get_opportunity_by_source_signal_id(signal_id)
        if existing is not None:
            response.status_code = status.HTTP_200_OK
            return existing

        opportunity = qualify_opportunity(signal)
        saved = signal_store.add_opportunity(opportunity)
        signal_store.update_signal(mark_signal_qualified(signal))
        return saved

    @app.post("/api/scans/{source}/run", response_model=ScanResponse)
    def run_scan(source: str, request: ScanRequest) -> ScanResponse:
        try:
            signals = signal_scanner.scan_source(source, query=request.query, limit=request.limit)
        except UnsupportedSignalSourceError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        except SourceNotConfiguredError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc
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

    @app.get("/api/profiles", response_model=ProfileListResponse)
    def list_profiles(x_vault_password: str | None = Header(default=None)) -> ProfileListResponse:
        password = require_vault_password(x_vault_password)
        try:
            profiles = profile_vault.list_profiles(password)
        except VaultPasswordError as exc:
            raise vault_error_to_http(exc) from exc
        return ProfileListResponse(items=profiles, count=len(profiles))

    @app.post(
        "/api/profiles",
        response_model=Profile,
        status_code=status.HTTP_201_CREATED,
    )
    def create_profile(
        profile: Profile,
        x_vault_password: str | None = Header(default=None),
    ) -> Profile:
        password = require_vault_password(x_vault_password)
        try:
            return profile_vault.add_profile(profile, password)
        except VaultPasswordError as exc:
            raise vault_error_to_http(exc) from exc

    @app.get("/api/profiles/{profile_id}", response_model=Profile)
    def get_profile(
        profile_id: str,
        x_vault_password: str | None = Header(default=None),
    ) -> Profile:
        password = require_vault_password(x_vault_password)
        try:
            profile = profile_vault.get_profile(profile_id, password)
        except VaultPasswordError as exc:
            raise vault_error_to_http(exc) from exc
        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile not found: {profile_id}",
            )
        return profile

    return app


app = create_app()
