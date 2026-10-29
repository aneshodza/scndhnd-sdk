import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

from anibis_sdk import AnibisClient
from tutti_sdk import TuttiClient

Platform = Literal["tutti", "anibis"]

PLATFORMS: tuple[Platform, ...] = ("tutti", "anibis")

_CLIENTS: dict[str, Callable[[], TuttiClient]] = {"tutti": TuttiClient, "anibis": AnibisClient}
_SITES = {"tutti": "https://www.tutti.ch", "anibis": "https://www.anibis.ch"}


@dataclass(frozen=True)
class Listing:
    """One listing in the same shape for every marketplace."""

    platform: Platform
    id: str
    title: str
    #: Price in CHF. ``0`` for free items, ``None`` when the site shows no number.
    price: float | None
    #: The price as the site shows it, e.g. ``"1'200.-"`` or ``"Gratis"``.
    price_text: str
    url: str
    image_url: str | None
    #: Postcode and place, e.g. ``"8001 Zürich"``.
    location: str | None
    category: str | None
    posted_at: datetime | None
    #: Only filled by :func:`get_listing`; search results have no description.
    description: str | None = None


def search(
    query: str,
    *,
    min_price: float | None = None,
    max_price: float | None = None,
    platforms: tuple[Platform, ...] | list[Platform] = PLATFORMS,
) -> list[Listing]:
    """Search several marketplaces and return the first page of each, newest first.

    tutti.ch and anibis.ch show some of each other's listings. When both are
    searched, a listing that appears on both is returned once, from tutti.
    """
    results: list[Listing] = []
    for platform in platforms:
        with _CLIENTS[platform]() as client:
            builder = client.search(query)
            if min_price is not None or max_price is not None:
                builder.price(min=min_price, max=max_price)
            results += [_to_listing(platform, raw) for raw in builder.fetch().listings]

    seen: set[tuple[str, str, str | None]] = set()
    unique = []
    for listing in results:
        key = (listing.title, listing.price_text, listing.location)
        if key not in seen:
            seen.add(key)
            unique.append(listing)
    return sorted(unique, key=lambda l: l.posted_at or datetime.min.astimezone(), reverse=True)


def get_listing(platform: Platform, listing_id: str) -> Listing:
    """Fetch one listing with its description."""
    with _CLIENTS[platform]() as client:
        raw = client.listings.get(listing_id)
    return _to_listing(platform, raw, description=raw.get("body"))


def parse_price(text: str | None) -> float | None:
    """Turn a displayed price like ``"1'200.-"`` or ``"Gratis"`` into CHF."""
    if not text:
        return None
    if text.strip().lower() == "gratis":
        return 0.0
    match = re.search(r"\d[\d']*(?:\.\d{1,2})?", text)
    return float(match.group().replace("'", "")) if match else None


def _to_listing(platform: Platform, raw: dict[str, Any], description: str | None = None) -> Listing:
    postcode = raw.get("postcodeInformation") or {}
    place = " ".join(p for p in (postcode.get("postcode"), postcode.get("locationName")) if p)
    image = (raw.get("thumbnail") or {}).get("rendition") or {}
    timestamp = raw.get("timestamp")
    return Listing(
        platform=platform,
        id=raw["listingID"],
        title=raw.get("title") or "",
        price=parse_price(raw.get("formattedPrice")),
        price_text=raw.get("formattedPrice") or "",
        url=f"{_SITES[platform]}/de/vi/{raw['listingID']}",
        image_url=image.get("src"),
        location=place or None,
        category=(raw.get("primaryCategory") or {}).get("label"),
        posted_at=datetime.fromisoformat(timestamp) if timestamp else None,
        description=description,
    )
