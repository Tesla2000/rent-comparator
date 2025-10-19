from __future__ import annotations

import json
from typing import ClassVar

import httpx
from bs4 import BeautifulSoup
from pydantic import HttpUrl
from pydantic import NonNegativeInt
from pydantic_settings import BaseSettings

from .base import OfferData
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
    n_promoted_messages: NonNegativeInt = 0

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

    def _fetch_offer_page(self, client: httpx.Client, href: str) -> OfferData:
        """Fetch and parse Otodom offer page from MainContent div."""
        if href.startswith("http"):
            offer_url = href
        else:
            offer_url = f"{self.base_url}{href}"

        # Fetch the offer page
        offer_response = client.get(offer_url)
        offer_response.raise_for_status()

        # Parse and clean the offer page
        offer_soup = BeautifulSoup(offer_response.content, "lxml")

        description = json.loads(
            offer_soup.find("script", {"id": "__NEXT_DATA__"}).get_text()
        )["props"]["pageProps"]["ad"]["description"]
        # Remove script and style elements
        for script in offer_soup(["style", "scripts"]):
            script.decompose()

        # Get text and clean it
        text = offer_soup.get_text(separator="\n")

        return OfferData(url=offer_url, text=text + description)


class _CityToVoivodeship(BaseSettings):
    city_to_voivodeship: dict[str, str] = {"wroclaw": "dolnoslaskie"}
