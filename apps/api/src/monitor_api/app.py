from __future__ import annotations

from dataclasses import dataclass, field

from fastapi import FastAPI, status
from pydantic import BaseModel

from monitor_api import __version__
from monitor_api.models import Opportunity, ProjectSignal


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


@dataclass
class InMemoryStore:
    signals: list[ProjectSignal] = field(default_factory=list)
    opportunities: list[Opportunity] = field(default_factory=list)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Monitor API",
        version=__version__,
        description=(
            "Local API for Monitor signal discovery, qualification, "
            "and risk/autopilot contracts."
        ),
    )
    store = InMemoryStore()

    @app.get("/api/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(service="monitor-api", status="ok", version=__version__)

    @app.get("/api/signals", response_model=ProjectSignalListResponse)
    def list_signals() -> ProjectSignalListResponse:
        return ProjectSignalListResponse(items=store.signals, count=len(store.signals))

    @app.post(
        "/api/signals",
        response_model=ProjectSignal,
        status_code=status.HTTP_201_CREATED,
    )
    def create_signal(signal: ProjectSignal) -> ProjectSignal:
        store.signals.append(signal)
        return signal

    @app.get("/api/opportunities", response_model=OpportunityListResponse)
    def list_opportunities() -> OpportunityListResponse:
        return OpportunityListResponse(items=store.opportunities, count=len(store.opportunities))

    @app.post(
        "/api/opportunities",
        response_model=Opportunity,
        status_code=status.HTTP_201_CREATED,
    )
    def create_opportunity(opportunity: Opportunity) -> Opportunity:
        store.opportunities.append(opportunity)
        return opportunity

    return app


app = create_app()
