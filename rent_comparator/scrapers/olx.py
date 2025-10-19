from __future__ import annotations

from typing import ClassVar

from pydantic import HttpUrl

from .base import Website
from .sort_params import SortDirection
from .sort_params import SortField
from .website_type import WebsiteType


class OLXWebsite(Website):
    """OLX.pl - popular classifieds site."""

    website_type: ClassVar[WebsiteType] = WebsiteType.OLX
    name: ClassVar[str] = "OLX"
    base_url: ClassVar[HttpUrl] = "https://www.olx.pl"
    search_path: ClassVar[str] = (
        "/nieruchomosci/stancje-pokoje/{city}/?page={page}"
    )
    offer_selector: ClassVar[str] = 'a[class="css-1tqlkj0"]'

    @staticmethod
    def _get_sorting_parameters(
        sort_field: SortField | None = None,
        sort_direction: SortDirection | None = None,
    ) -> list[str]:
        query_params = []
        if sort_field is not None:
            if sort_field != SortField.PRICE:
                raise ValueError(
                    f"Sort field other than {SortField.PRICE.value} not defined. Please define then or use {SortField.PRICE.value}"
                )
            if sort_direction is None:
                raise ValueError(
                    "Sort direction must be provided if sort field is"
                )
            query_params.append(
                f"search%5Border%5D=filter_float_price%3A{sort_direction.value.lower()}"
            )
        return query_params
