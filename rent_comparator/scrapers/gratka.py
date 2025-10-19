from __future__ import annotations

from typing import ClassVar

from pydantic import HttpUrl

from .base import Website
from .sort_params import SortDirection
from .sort_params import SortField
from .website_type import WebsiteType


class GratkaWebsite(Website):
    """Gratka.pl - another Polish real estate portal."""

    website_type: ClassVar[WebsiteType] = WebsiteType.GRATKA
    name: ClassVar[str] = "Gratka"
    base_url: ClassVar[HttpUrl] = "https://gratka.pl"
    search_path: ClassVar[str] = "/nieruchomosci/pokoje/{city}?page={page}"
    offer_selector: ClassVar[str] = 'a[class="_0NFK4W undefined"]'

    @staticmethod
    def _get_sorting_parameters(
        sort_field: SortField | None = None,
        sort_direction: SortDirection | None = None,
    ) -> list[str]:
        if sort_field is not None or sort_direction is not None:
            raise ValueError("Sorting not implemented")
        return []
