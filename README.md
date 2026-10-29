# scndhnd-sdk

Python SDKs for Swiss second-hand marketplaces, in one install.

Each marketplace has its own package. `scndhnd-sdk` depends on all of them, re-exports their clients and adds one search across all marketplaces.

| Marketplace | Package | Client | Docs |
| --- | --- | --- | --- |
| [tutti.ch](https://www.tutti.ch) | [`tutti-sdk`](https://github.com/aneshodza/tutti-sdk) | `TuttiClient` | [docs](https://aneshodza.github.io/tutti-sdk/) |
| [anibis.ch](https://www.anibis.ch) | [`anibis-sdk`](https://github.com/aneshodza/anibis-sdk) | `AnibisClient` | [docs](https://aneshodza.github.io/anibis-sdk/) |

> ⚠️ Not affiliated with any of these marketplaces. Respect their terms of service and rate limits.

## Install

```sh
pip install scndhnd-sdk    # or: uv add scndhnd-sdk
```

If you need only one marketplace, install its package directly, e.g. `pip install tutti-sdk`.

## Usage

Search every marketplace at once:

```python
from scndhnd_sdk import get_listing, search

for listing in search("brompton", max_price=1200):
    print(listing.platform, listing.price, listing.title, listing.url)

detail = get_listing("tutti", "83843696")  # adds the description
```

Each call returns the first page per marketplace, newest first, as `Listing` objects with the same fields everywhere. A listing shown on both tutti and anibis is returned once.

For filters beyond price, use a marketplace's own client:

```python
from scndhnd_sdk import AnibisClient, TuttiClient

for client_cls in (TuttiClient, AnibisClient):
    with client_cls() as client:
        result = client.search("velo").price(max=300).fetch()
        print(client_cls.__name__, result.total_count)
```

Both clients share the same search builder and result API, documented in the [tutti-sdk docs](https://aneshodza.github.io/tutti-sdk/).

## Development

```sh
uv sync
uv run pytest            # offline unit tests
uv run pytest -m live    # + one live search per marketplace
```

Commits follow [Conventional Commits](https://www.conventionalcommits.org/). [release-please](https://github.com/googleapis/release-please) keeps a release PR open on `main`. Merging it tags the release, publishes to PyPI, and deploys the API docs to GitHub Pages.
