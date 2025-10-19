from __future__ import annotations

from typing import ClassVar

from pydantic import HttpUrl
from pydantic_settings import BaseSettings

from .base import Website
from .sort_params import SortDirection
from .sort_params import SortField
from .website_type import WebsiteType


class OtodomWebsite(Website):
    """Otodom.pl - main Polish real estate portal."""

    website_type: ClassVar[WebsiteType] = WebsiteType.OTODOM
    name: ClassVar[str] = "Otodom"
    base_url: ClassVar[HttpUrl] = "https://www.otodom.pl"
    search_path: ClassVar[str] = (
        "/pl/wyniki/wynajem/pokoj/{voivodeship}/{city}/{city}/{city}?page={page}"
    )
    offer_selector: ClassVar[str] = "a[data-cy='listing-item-link']"

    def get_search_url(
        self,
        city: str,
        page: int = 1,
        sort_field: SortField | None = None,
        sort_direction: SortDirection | None = None,
    ) -> str:
        return (
            super()
            .get_search_url(city, page, sort_field, sort_direction)
            .replace(
                "{voivodeship}", _CityToVoivodeship().city_to_voivodeship[city]
            )
        )


class _CityToVoivodeship(BaseSettings):
    city_to_voivodeship: dict[str, str] = {"wroclaw": "dolnośląskie"}
