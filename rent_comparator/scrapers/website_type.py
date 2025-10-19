from __future__ import annotations

from enum import Enum


class WebsiteType(str, Enum):
    """Enum for available rental website types."""

    OTODOM = "otodom"
    OLX = "olx"
    GRATKA = "gratka"
