from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic import model_validator
from pydantic import PositiveFloat
from pydantic import PositiveInt
from pydantic_settings import BaseSettings
from pydantic_settings import CliApp
from pydantic_settings import SettingsConfigDict

from .criteria import FilterParams
from .criteria import FilterType
from .criteria import SearchCriteria
from .finder import BestOfferFinder


class ExperimentSettings(BaseSettings):
    """Settings for running best offer experiments."""

    data_folder: Path = Field(
        default=Path("rent_comparator/data/extracted_parameters"),
        description="Folder with extracted offer parameters",
    )
    criteria: SearchCriteria = Field(
        default=SearchCriteria.TOTAL_COST, description="Search criteria"
    )
    filters: list[FilterType] = Field(
        default_factory=list, description="Filters to apply"
    )
    exclude_locations: list[str] = Field(
        default_factory=list, description="Locations to exclude from results"
    )
    include_locations: list[str] = Field(
        default_factory=list, description="Locations to include in results"
    )
    exclude_offers: dict[str, str] = Field(
        default_factory=dict,
        description="Offers to exclude by filename with reason (e.g., {'offer_1.json': 'duplicate'})",
    )
    top_n: PositiveInt = Field(
        default=10, description="Number of top offers to show"
    )
    min_rent: PositiveFloat = Field(
        default=500.0, description="Minimum rent price (outlier filter)"
    )
    max_rent: PositiveFloat = Field(
        default=10000.0, description="Maximum rent price (outlier filter)"
    )
    min_area: PositiveFloat = Field(
        default=5.0, description="Minimum area in m² (outlier filter)"
    )
    max_area: PositiveFloat = Field(
        default=30.0, description="Maximum area in m² (outlier filter)"
    )

    model_config = SettingsConfigDict(
        cli_parse_args=True,
        env_file=".env",
        extra="ignore",
        cli_kebab_case=True,
        cli_ignore_unknown_args=True,
    )

    @model_validator(mode="after")
    def validate_location_filters(self) -> ExperimentSettings:
        """Ensure include_locations and exclude_locations are not both provided."""
        if self.include_locations and self.exclude_locations:
            raise ValueError(
                "Cannot specify both --include-locations and --exclude-locations"
            )
        return self

    def cli_cmd(self) -> None:
        """Run experiment to find best offers."""
        print("=== Finding Best Offers ===")
        print(f"Criteria: {self.criteria.value}")
        print(f"Filters: {[f.value for f in self.filters]}")
        if self.exclude_locations:
            print(f"Exclude locations: {self.exclude_locations}")
        if self.include_locations:
            print(f"Include locations: {self.include_locations}")
        if self.exclude_offers:
            print(f"Exclude offers: {self.exclude_offers}")
        print(
            f"Outlier filters: rent {self.min_rent}-{self.max_rent} PLN, area {self.min_area}-{self.max_area} m²"
        )
        print(f"Top N: {self.top_n}\n")

        finder = BestOfferFinder(
            self.data_folder,
            min_rent=self.min_rent,
            max_rent=self.max_rent,
            min_area=self.min_area,
            max_area=self.max_area,
        )
        finder.load_offers()

        print(
            f"Loaded {len(finder.offers)} offers (after outlier filtering)\n"
        )

        filter_params = FilterParams(
            filters=self.filters,
            exclude_locations=(
                self.exclude_locations if self.exclude_locations else None
            ),
            include_locations=(
                self.include_locations if self.include_locations else None
            ),
            exclude_offers=self.exclude_offers,
        )

        best_offers = finder.find_best(
            criteria=self.criteria,
            filter_params=filter_params,
            top_n=self.top_n,
        )

        print(f"=== Top {len(best_offers)} Offers ===\n")

        for i, offer in enumerate(best_offers, start=1):
            print(f"{i}. [{offer.source}] {offer.file_name}")
            print(f"   URL: {offer.url}")
            print(f"   Rent: {offer.parameters.rent_price} PLN")
            print(f"   Other costs: {offer.parameters.other_prices} PLN")
            print(f"   Total: {offer.total_cost} PLN")

            if offer.parameters.area:
                print(f"   Area: {offer.parameters.area} m²")
            if offer.cost_per_meter:
                print(f"   Cost/m²: {offer.cost_per_meter:.2f} PLN/m²")

            if offer.parameters.address:
                print(f"   Address: {offer.parameters.address}")
            elif offer.parameters.location:
                print(f"   Location: {offer.parameters.location}")

            if offer.parameters.deposit:
                print(f"   Deposit: {offer.parameters.deposit} PLN")
            if offer.parameters.minimal_rent_duration_months:
                print(
                    f"   Min duration: {offer.parameters.minimal_rent_duration_months} months"
                )

            if offer.parameters.only_for_students:
                print("   ⚠ Only for students")
            if offer.parameters.only_for_woman:
                print("   ⚠ Only for women")

            print()


if __name__ == "__main__":
    CliApp.run(ExperimentSettings)
