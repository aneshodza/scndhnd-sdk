"""Python SDKs for Swiss second-hand marketplaces in one install.

Each marketplace has its own package; this one depends on all of them and
re-exports their clients:

- :class:`TuttiClient` for tutti.ch, from
  `tutti-sdk <https://aneshodza.github.io/tutti-sdk/>`_
- :class:`AnibisClient` for anibis.ch, from
  `anibis-sdk <https://aneshodza.github.io/anibis-sdk/>`_
"""

__docformat__ = "restructuredtext"

from anibis_sdk import AnibisClient
from tutti_sdk import TuttiClient

__all__ = ["AnibisClient", "TuttiClient"]
