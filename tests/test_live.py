"""One live search per marketplace. Run with ``pytest -m live``."""

import pytest

from scndhnd_sdk import AnibisClient, TuttiClient, get_listing, search

pytestmark = pytest.mark.live


@pytest.mark.parametrize("client_cls", [TuttiClient, AnibisClient])
def test_search(client_cls):
    with client_cls() as client:
        result = client.search("velo").fetch()
    assert result.total_count > 1000
    assert result.listings[0]["listingID"]


def test_search_all_marketplaces():
    listings = search("velo", max_price=500)
    assert {l.platform for l in listings} == {"tutti", "anibis"}
    assert all(l.price is None or l.price <= 500 for l in listings)
    detail = get_listing(listings[0].platform, listings[0].id)
    assert detail.description
