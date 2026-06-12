from __future__ import annotations

import re
from dataclasses import dataclass

from monitor_api.models import Opportunity, OpportunityStatus, ProjectSignal, SignalStatus


@dataclass(frozen=True)
class QualificationScores:
    python_fit_score: float
    web3_fit_score: float
    buyer_intent_score: float
    urgency_score: float
    budget_quality_score: float
    response_likelihood_score: float
    scam_risk_score: float


def score_signal(signal: ProjectSignal) -> QualificationScores:
    text = _combined_signal_text(signal)
    keywords = {keyword.lower() for keyword in signal.detected_keywords}

    python_fit = _score_keywords(
        text,
        keywords,
        strong={"python", "fastapi", "django", "flask", "pydantic", "pytest", "automation"},
        weak={"backend", "api", "etl", "scraper", "dashboard", "data"},
    )
    web3_fit = _score_keywords(
        text,
        keywords,
        strong={"web3", "crypto", "wallet", "blockchain", "ethereum", "solidity", "defi"},
        weak={"token", "nft", "dao", "smart contract", "onchain", "chain"},
    )
    if web3_fit >= 0.4 and python_fit >= 0.7:
        web3_fit = _clamp(web3_fit + 0.3)
    buyer_intent = _score_keywords(
        text,
        keywords,
        strong={"hiring", "hire", "need", "looking for", "contract", "paid", "build"},
        weak={"help", "developer", "dev", "proposal", "application", "apply"},
    )
    if any(phrase in text for phrase in ["no budget", "just browsing", "maybe someday"]):
        buyer_intent = min(buyer_intent, 0.35)
    urgency = _score_keywords(
        text,
        keywords,
        strong={"asap", "urgent", "today", "this week", "immediately", "start now"},
        weak={"soon", "deadline", "quick", "fast", "start"},
    )
    budget_quality = _budget_score(text, signal.budget_hint)
    response_likelihood = _response_likelihood_score(text, signal)
    scam_risk = _score_keywords(
        text,
        keywords,
        strong={
            "seed phrase",
            "private key",
            "pay upfront",
            "guaranteed",
            "10x",
            "verification fee",
        },
        weak={"release funds", "wire", "telegram only", "no contract", "deposit", "airdrop"},
    )

    return QualificationScores(
        python_fit_score=python_fit,
        web3_fit_score=web3_fit,
        buyer_intent_score=buyer_intent,
        urgency_score=urgency,
        budget_quality_score=budget_quality,
        response_likelihood_score=response_likelihood,
        scam_risk_score=scam_risk,
    )


def qualify_opportunity(signal: ProjectSignal) -> Opportunity:
    scores = score_signal(signal)
    return Opportunity(
        source_signal_id=signal.id,
        source_platform=signal.source_platform,
        source_id=signal.source_id,
        source_url=signal.source_url,
        title=signal.title,
        description=signal.raw_text,
        required_skills=_extract_required_skills(signal),
        budget_min=_extract_budget_amount(signal.budget_hint or signal.raw_text),
        budget_max=_extract_budget_amount(signal.budget_hint or signal.raw_text),
        contact_route=signal.contact_route,
        status=OpportunityStatus.QUALIFIED,
        python_fit_score=scores.python_fit_score,
        web3_fit_score=scores.web3_fit_score,
        buyer_intent_score=scores.buyer_intent_score,
        budget_quality_score=scores.budget_quality_score,
        urgency_score=scores.urgency_score,
        response_likelihood_score=scores.response_likelihood_score,
        scam_risk_score=scores.scam_risk_score,
    )


def mark_signal_qualified(signal: ProjectSignal) -> ProjectSignal:
    signal.status = SignalStatus.QUALIFIED
    return signal


def _combined_signal_text(signal: ProjectSignal) -> str:
    parts = [signal.title, signal.raw_text, signal.project_name or "", signal.budget_hint or ""]
    parts.extend(signal.detected_keywords)
    return " ".join(parts).lower()


def _score_keywords(
    text: str,
    explicit_keywords: set[str],
    *,
    strong: set[str],
    weak: set[str],
) -> float:
    strong_hits = sum(1 for keyword in strong if keyword in text or keyword in explicit_keywords)
    weak_hits = sum(1 for keyword in weak if keyword in text or keyword in explicit_keywords)
    return _clamp(strong_hits * 0.40 + weak_hits * 0.15)


def _budget_score(text: str, budget_hint: str | None) -> float:
    budget_text = f"{text} {budget_hint or ''}".lower()
    if any(keyword in budget_text for keyword in ["no budget", "unpaid", "equity only", "free"]):
        return 0.0
    if _extract_budget_amount(budget_text) is not None:
        return 0.9
    if any(keyword in budget_text for keyword in ["budget", "paid", "rate", "contract"]):
        return 0.55
    return 0.1


def _response_likelihood_score(text: str, signal: ProjectSignal) -> float:
    score = 0.2
    if signal.contact_route.value != "none":
        score += 0.35
    if any(keyword in text for keyword in ["apply", "proposal", "dm", "email", "contact", "send"]):
        score += 0.25
    if signal.source_url is not None:
        score += 0.1
    if signal.source_platform.value in {"upwork", "fiverr", "dework", "gitcoin"}:
        score += 0.2
    return _clamp(score)


def _extract_required_skills(signal: ProjectSignal) -> list[str]:
    text = _combined_signal_text(signal)
    ordered_keywords = [
        "python",
        "fastapi",
        "django",
        "flask",
        "pydantic",
        "pytest",
        "automation",
        "web3",
        "crypto",
        "wallet",
        "blockchain",
        "ethereum",
        "solidity",
        "defi",
    ]
    skills = [keyword for keyword in ordered_keywords if keyword in text]
    return list(dict.fromkeys(skills))


def _extract_budget_amount(text: str | None) -> float | None:
    if not text:
        return None
    match = re.search(r"(?:\$|usd\s*)\s*([0-9][0-9,]*(?:\.\d+)?)", text.lower())
    if match is None:
        return None
    return float(match.group(1).replace(",", ""))


def _clamp(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 4)
