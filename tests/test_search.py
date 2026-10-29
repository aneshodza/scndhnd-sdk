"""Offline tests for the cross-marketplace search, using recorded responses."""

import json
from datetime import datetime
from pathlib import Path

import httpx
import pytest

import scndhnd_sdk
from scndhnd_sdk import AnibisClient, TuttiClient, get_listing, listings, parse_price, search

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def requests(monkeypatch):
    """Serve the recorded fixtures and record every request body."""
    seen: list[tuple[str, dict]] = []

    def factory(platform: str, client_cls):
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            seen.append((platform, body))
            name = "listing" if body["operationName"] == "GetListingDetails" else "search"
            return httpx.Response(
                200, json=json.loads((FIXTURES / f"{name}-{platform}.json").read_text())
            )

        return lambda: client_cls(transport=httpx.MockTransport(handler))

    monkeypatch.setattr(
        listings,
        "_CLIENTS",
        {"tutti": factory("tutti", TuttiClient), "anibis": factory("anibis", AnibisClient)},
    )
    return seen


@pytest.mark.parametrize(
    ("text", "price"),
    [
        ("1'200.-", 1200.0),
        ("650.-", 650.0),
        ("12.50", 12.5),
        ("Gratis", 0.0),
        ("", None),
        ("Auf Anfrage", None),
    ],
)
def test_parse_price(text, price):
    assert parse_price(text) == price


def test_search_normalizes_listings(requests):
    listings = search("brompton", platforms=["tutti"])

    first = next(l for l in listings if l.id == "83843696")
    assert first.platform == "tutti"
    assert first.title == "Brompton C-Line M6R Light Gray"
    assert first.price == 1200.0
    assert first.price_text == "1'200.-"
    assert first.url == "https://www.tutti.ch/de/vi/83843696"
    assert first.image_url.startswith("https://c.tutti.ch/")
    assert first.location == "1004 Lausanne"
    assert first.category == "Velos"
    assert first.posted_at.tzinfo is not None
    assert first.description is None


def test_search_merges_sites_newest_first_without_duplicates(requests):
    listings = search("brompton")

    assert [p for p, _ in requests] == ["tutti", "anibis"]
    titles = [l.title for l in listings]
    assert titles.count("Brompton C-Line M6R Light Gray") == 1
    assert (
        next(l for l in listings if l.title == "Brompton C-Line M6R Light Gray").platform == "tutti"
    )
    assert any(l.platform == "anibis" for l in listings)
    dates = [l.posted_at for l in listings]
    assert dates == sorted(dates, reverse=True)


def test_search_sends_price_filter(requests):
    search("brompton", min_price=100, max_price=900, platforms=["anibis"])

    prices = requests[0][1]["variables"]["constraints"]["prices"]
    assert prices == [{"key": "price", "freeOnly": False, "min": 100, "max": 900}]


def test_search_without_price_sends_no_price_filter(requests):
    search("brompton", platforms=["tutti"])

    assert requests[0][1]["variables"]["constraints"]["prices"] == []


def test_get_listing_includes_description(requests):
    listing = get_listing("tutti", "83843696")

    assert listing.description.startswith("Condition: excellent")
    assert listing.price == 1200.0
    assert isinstance(listing.posted_at, datetime)


def test_get_listing_raises_for_removed_listing(monkeypatch):
    handler = lambda request: httpx.Response(200, json={"data": {"listing": None}})
    monkeypatch.setitem(
        listings._CLIENTS, "tutti", lambda: TuttiClient(transport=httpx.MockTransport(handler))
    )
    with pytest.raises(LookupError):
        get_listing("tutti", "1")


def test_package_exports():
    assert scndhnd_sdk.PLATFORMS == ("tutti", "anibis")
    assert scndhnd_sdk.Listing is listings.Listing
    assert issubclass(scndhnd_sdk.TuttiError, Exception)
