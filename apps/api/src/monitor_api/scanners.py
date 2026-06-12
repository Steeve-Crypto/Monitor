from __future__ import annotations

import hashlib
import os
from collections.abc import Callable
from dataclasses import dataclass
from html import unescape
from urllib.parse import urlparse
from urllib.request import urlopen
from xml.etree import ElementTree

from monitor_api.models import ContactRoute, Platform, ProjectSignal, RiskLevel, SignalKind

CRYPTO_RSS_FEED_URL_ENV = "MONITOR_CRYPTO_RSS_FEED_URL"


class UnsupportedSignalSourceError(ValueError):
    def __init__(self, source: str) -> None:
        super().__init__(f"Unsupported signal source: {source}")
        self.source = source


class SignalAdapter:
    source: str
    platform: Platform

    def scan(self, query: str, limit: int = 10) -> list[ProjectSignal]:
        raise NotImplementedError


@dataclass(frozen=True)
class MockSignalAdapter(SignalAdapter):
    source: str = "mock"
    platform: Platform = Platform.OTHER
    signal_kind: SignalKind = SignalKind.OTHER
    contact_route: ContactRoute = ContactRoute.NONE
    risk_level: RiskLevel = RiskLevel.LOW

    def scan(self, query: str, limit: int = 10) -> list[ProjectSignal]:
        normalized_limit = normalize_limit(limit)
        keywords = _extract_keywords(query)
        return [
            ProjectSignal(
                source_platform=self.platform,
                source_id=f"{self.source}-{index + 1}",
                title=f"{query} lead #{index + 1}",
                raw_text=(
                    f"Mock {self.source} signal for '{query}'. "
                    "Potential Python/web3 project opportunity."
                ),
                signal_kind=self.signal_kind,
                detected_keywords=keywords,
                contact_route=self.contact_route,
                risk_level=self.risk_level,
            )
            for index in range(normalized_limit)
        ]


class XSignalAdapter(MockSignalAdapter):
    def __init__(self) -> None:
        super().__init__(
            source="x",
            platform=Platform.X,
            signal_kind=SignalKind.BUYING_INTENT,
            contact_route=ContactRoute.PUBLIC_REPLY,
            risk_level=RiskLevel.LOW,
        )


class DiscordSignalAdapter(MockSignalAdapter):
    def __init__(self) -> None:
        super().__init__(
            source="discord",
            platform=Platform.DISCORD,
            signal_kind=SignalKind.HIRING,
            contact_route=ContactRoute.DISCORD_CHANNEL,
            risk_level=RiskLevel.LOW,
        )


class MarketplaceSignalAdapter(MockSignalAdapter):
    def __init__(self) -> None:
        super().__init__(
            source="marketplaces",
            platform=Platform.UPWORK,
            signal_kind=SignalKind.HIRING,
            contact_route=ContactRoute.PLATFORM_PROPOSAL,
            risk_level=RiskLevel.MEDIUM,
        )


class CryptoSignalAdapter(MockSignalAdapter):
    def __init__(self) -> None:
        super().__init__(
            source="crypto",
            platform=Platform.WEB3_CAREER,
            signal_kind=SignalKind.BOUNTY,
            contact_route=ContactRoute.APPLICATION_FORM,
            risk_level=RiskLevel.LOW,
        )


@dataclass(frozen=True)
class CryptoRssSignalAdapter(SignalAdapter):
    feed_url: str | None = None
    fetch_feed: Callable[[str], str] = None  # type: ignore[assignment]
    source: str = "crypto_rss"
    platform: Platform = Platform.RSS

    def __post_init__(self) -> None:
        if self.fetch_feed is None:
            object.__setattr__(self, "fetch_feed", fetch_text)

    def scan(self, query: str, limit: int = 10) -> list[ProjectSignal]:
        feed_url = self.feed_url or os.getenv(CRYPTO_RSS_FEED_URL_ENV)
        if not feed_url:
            return []

        query_keywords = _extract_keywords(query)
        raw_feed = self.fetch_feed(feed_url)
        entries = parse_rss_items(raw_feed)
        signals: list[ProjectSignal] = []
        for entry in entries:
            searchable_text = f"{entry.title} {entry.description}".lower()
            if query_keywords and not any(keyword in searchable_text for keyword in query_keywords):
                continue
            signals.append(
                ProjectSignal(
                    source_platform=self.platform,
                    source_id=entry.stable_id,
                    source_url=entry.link or None,
                    title=entry.title,
                    raw_text=entry.description or entry.title,
                    signal_kind=SignalKind.HIRING,
                    detected_keywords=query_keywords,
                    contact_route=ContactRoute.APPLICATION_FORM,
                    risk_level=RiskLevel.LOW,
                )
            )
            if len(signals) >= normalize_limit(limit):
                break
        return signals


@dataclass(frozen=True)
class RssItem:
    title: str
    link: str | None
    guid: str | None
    description: str

    @property
    def stable_id(self) -> str:
        if self.guid:
            return self.guid
        source_value = self.link or self.title
        return hashlib.sha256(source_value.encode("utf-8")).hexdigest()[:16]


@dataclass
class SignalMeshScanner:
    adapters: dict[str, SignalAdapter]

    @classmethod
    def with_default_adapters(
        cls,
        *,
        crypto_rss_feed_url: str | None = None,
        crypto_rss_fetcher: Callable[[str], str] | None = None,
    ) -> SignalMeshScanner:
        adapters: list[SignalAdapter] = [
            XSignalAdapter(),
            DiscordSignalAdapter(),
            MarketplaceSignalAdapter(),
            CryptoSignalAdapter(),
            CryptoRssSignalAdapter(
                feed_url=crypto_rss_feed_url,
                fetch_feed=crypto_rss_fetcher or fetch_text,
            ),
        ]
        return cls(adapters={adapter.source: adapter for adapter in adapters})

    def get_adapter(self, source: str) -> SignalAdapter:
        try:
            return self.adapters[source]
        except KeyError as exc:
            raise UnsupportedSignalSourceError(source) from exc

    def scan_source(self, source: str, query: str, limit: int = 10) -> list[ProjectSignal]:
        return self.get_adapter(source).scan(query=query, limit=limit)


def parse_rss_items(raw_feed: str) -> list[RssItem]:
    root = ElementTree.fromstring(raw_feed)
    items: list[RssItem] = []
    for item in root.findall(".//item"):
        title = _child_text(item, "title") or "Untitled crypto job"
        link = _child_text(item, "link")
        guid = _child_text(item, "guid")
        description = _child_text(item, "description") or title
        items.append(
            RssItem(
                title=unescape(title).strip(),
                link=link.strip() if link else None,
                guid=guid.strip() if guid else None,
                description=unescape(description).strip(),
            )
        )
    return items


def fetch_text(url: str) -> str:
    parsed_url = urlparse(url)
    if parsed_url.scheme not in {"http", "https"}:
        raise ValueError("Only http and https RSS feed URLs are allowed")
    with urlopen(url, timeout=10) as response:  # noqa: S310 - operator-configured public feed URL
        return response.read().decode("utf-8", errors="replace")


def normalize_limit(limit: int) -> int:
    return max(0, min(limit, 50))


def _child_text(item: ElementTree.Element, tag: str) -> str | None:
    child = item.find(tag)
    if child is None or child.text is None:
        return None
    return child.text


def _extract_keywords(query: str) -> list[str]:
    stop_words = {"a", "an", "and", "for", "in", "need", "of", "or", "the", "to", "with"}
    words = [word.strip(".,!?;:()[]{}\"'").lower() for word in query.split()]
    return [word for word in words if len(word) >= 2 and word not in stop_words]
