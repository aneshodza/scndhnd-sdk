"""Python SDKs for Swiss second-hand marketplaces in one install.

:func:`search` looks through every marketplace at once and returns
:class:`Listing` objects in one shape. :func:`get_listing` fetches a single
listing with its description.

Each marketplace also has its own package, re-exported here for everything
beyond search:

- :class:`TuttiClient` for tutti.ch, from
  `tutti-sdk <https://aneshodza.github.io/tutti-sdk/>`_
- :class:`AnibisClient` for anibis.ch, from
  `anibis-sdk <https://aneshodza.github.io/anibis-sdk/>`_
"""

__docformat__ = "restructuredtext"

from anibis_sdk import AnibisClient
from tutti_sdk import TuttiClient

from .listings import PLATFORMS, Listing, Platform, get_listing, parse_price, search

__all__ = [
    "PLATFORMS",
    "AnibisClient",
    "Listing",
    "Platform",
    "TuttiClient",
    "get_listing",
    "parse_price",
    "search",
]
