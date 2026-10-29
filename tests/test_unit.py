"""Offline tests against a mocked transport — no network."""

import httpx
import pytest

from scndhnd_sdk import AnibisClient, TuttiClient


@pytest.mark.parametrize(
    ("client_cls", "url"),
    [
        (TuttiClient, "https://api.tutti.ch/v10/graphql"),
        (AnibisClient, "https://www.anibis.ch/api/v10/graphql"),
    ],
)
def test_clients_talk_to_their_marketplace(client_cls, url):
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"data": {"searchLocalities": []}})

    with client_cls(transport=httpx.MockTransport(handler)) as client:
        assert client.localities.search("bern") == []
    assert str(seen[0].url) == url
