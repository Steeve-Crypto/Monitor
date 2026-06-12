from __future__ import annotations

import json
import os
from dataclasses import dataclass
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from monitor_api.models import ActionProposal, Application, ApplicationStatus

EXECUTOR_WEBHOOK_URL_ENV = "MONITOR_EXECUTOR_WEBHOOK_URL"


class ExternalExecutorError(RuntimeError):
    pass


class ExternalExecutorNotConfiguredError(ExternalExecutorError):
    pass


class ExternalExecutor:
    def execute(self, proposal: ActionProposal) -> Application:
        raise NotImplementedError


@dataclass(frozen=True)
class DisabledExternalExecutor(ExternalExecutor):
    def execute(self, proposal: ActionProposal) -> Application:
        raise ExternalExecutorNotConfiguredError(
            "External executor is not configured. Set a real executor adapter "
            "before executing sends/submissions."
        )


@dataclass(frozen=True)
class WebhookExternalExecutor(ExternalExecutor):
    webhook_url: str | None = None

    def execute(self, proposal: ActionProposal) -> Application:
        webhook_url = self.webhook_url or os.getenv(EXECUTOR_WEBHOOK_URL_ENV)
        if not webhook_url:
            raise ExternalExecutorNotConfiguredError(
                f"{EXECUTOR_WEBHOOK_URL_ENV} is required for webhook execution."
            )
        parsed = urlparse(webhook_url)
        if parsed.scheme not in {"http", "https"}:
            raise ExternalExecutorError("Only http and https executor webhook URLs are allowed.")

        payload = json.dumps(proposal.model_dump(mode="json")).encode("utf-8")
        request = Request(
            webhook_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=15) as response:  # noqa: S310 - operator-configured executor URL
            status = response.status
            body = response.read().decode("utf-8", errors="replace")[:500]
        if status >= 400:
            raise ExternalExecutorError(f"Executor webhook failed with status {status}: {body}")
        return Application(
            opportunity_id=str(proposal.payload_preview.get("opportunity_id", "unknown")),
            action_proposal_id=proposal.id,
            status=ApplicationStatus.SUBMITTED,
            outcome_notes=f"Executed via configured webhook with status {status}.",
        )
