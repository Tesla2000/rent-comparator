from __future__ import annotations

from collections.abc import Iterator
from typing import ClassVar
from typing import NamedTuple

import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel
from pydantic import HttpUrl

from .sort_params import SortDirection
from .sort_params import SortField
from .website_type import WebsiteType


class OfferData(NamedTuple):
    """Data scraped from a rental offer."""

    url: str
    text: str


class Website(BaseModel):
    """Base configuration for a rental listing website."""

    website_type: ClassVar[WebsiteType]
    name: ClassVar[str]
    base_url: ClassVar[HttpUrl]
    search_path: ClassVar[str]
    offer_selector: ClassVar[str]
    sort_field_param: ClassVar[str] = "by"
    sort_direction_param: ClassVar[str] = "direction"

    def get_search_url(
        self,
        city: str,
        page: int = 1,
        sort_field: SortField | None = None,
        sort_direction: SortDirection | None = None,
    ) -> str:
        """Generate search URL for the given page."""
        url = f"{self.base_url}{self.search_path}"
        url = url.replace("{city}", city)
        url = url.replace("{page}", str(page))

        query_params = self._get_sorting_parameters(sort_field, sort_direction)

        if query_params:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}{'&'.join(query_params)}"

        return url

    def _get_sorting_parameters(
        self,
        sort_field: SortField | None = None,
        sort_direction: SortDirection | None = None,
    ) -> list[str]:
        query_params = []
        if sort_field is not None:
            query_params.append(f"{self.sort_field_param}={sort_field.value}")
        if sort_direction is not None:
            query_params.append(
                f"{self.sort_direction_param}={sort_direction.value}"
            )
        return query_params

    def _fetch_offer_page(self, client: httpx.Client, href: str) -> OfferData:
        """Fetch and parse individual offer page content.

        Returns:
            OfferData with url and text, or None if error
        """
        if href.startswith("http"):
            offer_url = href
        else:
            offer_url = f"{self.base_url}{href}"

        # Fetch the offer page
        offer_response = client.get(offer_url)
        offer_response.raise_for_status()

        # Parse and clean the offer page
        offer_soup = BeautifulSoup(offer_response.content, "lxml")

        # Remove script and style elements
        for script in offer_soup(["script", "style"]):
            script.decompose()

        # Get text and clean it
        text = offer_soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (
            phrase.strip() for line in lines for phrase in line.split("  ")
        )
        text = "\n".join(chunk for chunk in chunks if chunk)

        return OfferData(url=offer_url, text=text)

    def scrape(
        self,
        city: str,
        max_pages: int = 10,
        sort_field: SortField | None = None,
        sort_direction: SortDirection | None = None,
    ) -> Iterator[OfferData]:
        """Generator that yields full text content for each offer."""
        client = httpx.Client(
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
            },
            timeout=30.0,
            follow_redirects=True,
        )

        try:
            for page in range(1, max_pages + 1):
                print(f"[{self.name}] Scraping page {page}/{max_pages}...")

                url = self.get_search_url(
                    city, page, sort_field, sort_direction
                )
                response = client.get(url)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, "lxml")

                # Find individual offer links
                offer_links = soup.select(self.offer_selector)

                if not offer_links:
                    print(
                        f"[{self.name}] No offers found on page {page}, stopping..."
                    )
                    break

                # Fetch and yield each offer's full page content
                for offer_link in offer_links:
                    href = offer_link.get("href")
                    if not href:
                        continue

                    offer_data = self._fetch_offer_page(client, href)
                    if offer_data:
                        yield offer_data

        finally:
            client.close()
