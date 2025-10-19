from __future__ import annotations

from .base import Website
from .gratka import GratkaWebsite
from .olx import OLXWebsite
from .otodom import OtodomWebsite
from .sort_params import SortDirection
from .sort_params import SortField
from .website_type import WebsiteType

# Build dictionary of available websites from their ClassVars
_WEBSITE_CLASSES = [OtodomWebsite, OLXWebsite, GratkaWebsite]
AVAILABLE_WEBSITES: dict[WebsiteType, type[Website]] = {
    cls.website_type: cls for cls in _WEBSITE_CLASSES
}

__all__ = [
    "Website",
    "WebsiteType",
    "OtodomWebsite",
    "OLXWebsite",
    "GratkaWebsite",
    "AVAILABLE_WEBSITES",
    "SortField",
    "SortDirection",
]
