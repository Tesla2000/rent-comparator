from __future__ import annotations

import json
from pathlib import Path

from pydantic import Field
from pydantic import PositiveInt
from pydantic_settings import BaseSettings
from pydantic_settings import CliApp
from rent_comparator.scrapers import AVAILABLE_WEBSITES
from rent_comparator.scrapers import SortDirection
from rent_comparator.scrapers import SortField
from rent_comparator.scrapers import WebsiteType


class ScraperSettings(BaseSettings):
    """CLI settings for rental scraper."""

    output_folder: Path = Field(
        default=Path("rent_comparator/data/rent_prices"),
        description="Folder to save scraped data",
    )
    city: str = Field(default="wroclaw", description="City to search in")
    max_pages: PositiveInt = Field(
        default=10, description="Maximum pages per website"
    )
    sources: list[WebsiteType] = Field(
        default_factory=lambda: list(AVAILABLE_WEBSITES.keys()),
        description="List of sources to scrape",
    )
    sort_field: SortField | None = Field(
        default=None, description="Field to sort by"
    )
    sort_direction: SortDirection | None = Field(
        default=None, description="Sort direction"
    )

    def cli_cmd(self) -> None:
        """Execute the scraping command."""
        # Ensure output folder exists
        self.output_folder.mkdir(parents=True, exist_ok=True)

        total_offers = 0

        # Scrape from selected websites
        for website_type in self.sources:
            website_cls = AVAILABLE_WEBSITES[website_type]
            website = website_cls()

            # Create source-specific folder
            source_folder = self.output_folder / website_type.value
            source_folder.mkdir(parents=True, exist_ok=True)

            print(f"\n=== Scraping {website.name} ===")

            for index, offer_data in enumerate(
                website.scrape(
                    city=self.city,
                    max_pages=self.max_pages,
                    sort_field=self.sort_field,
                    sort_direction=self.sort_direction,
                ),
                start=1,
            ):
                # Save each offer to a separate JSON file with URL and text
                offer_file = source_folder / f"{self.city}_offer_{index}.json"
                offer_json = {"url": offer_data.url, "text": offer_data.text}
                offer_file.write_text(
                    json.dumps(offer_json, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )

                total_offers += 1
                print(f"  Scraped offer {index} -> {offer_file}")

        print("\n=== Summary ===")
        print(f"Total offers scraped: {total_offers}")
        print(f"Results saved to: {self.output_folder}")


if __name__ == "__main__":
    s = CliApp.run(ScraperSettings)
