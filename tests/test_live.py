"""One live search per marketplace. Run with ``pytest -m live``."""

import pytest

from scndhnd_sdk import AnibisClient, TuttiClient

pytestmark = pytest.mark.live


@pytest.mark.parametrize("client_cls", [TuttiClient, AnibisClient])
def test_search(client_cls):
    with client_cls() as client:
        result = client.search("velo").fetch()
    assert result.total_count > 1000
    assert result.listings[0]["listingID"]
