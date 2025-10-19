from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel
from rent_comparator.extraction.models import OfferParameters

from .criteria import FilterParams
from .criteria import FilterType
from .criteria import SearchCriteria


class OfferResult(BaseModel):
    """Rental offer with computed metrics."""

    source: str
    file_name: str
    url: str
    parameters: OfferParameters
    total_cost: float
    cost_per_meter: float | None


class BestOfferFinder:
    """Finds best rental offers based on different criteria."""

    def __init__(
        self,
        data_folder: Path,
        min_rent: float = 100.0,
        max_rent: float = 10000.0,
        min_area: float = 5.0,
        max_area: float = 100.0,
    ):
        self.data_folder = data_folder
        self.min_rent = min_rent
        self.max_rent = max_rent
        self.min_area = min_area
        self.max_area = max_area
        self.offers: list[OfferResult] = []

    def load_offers(self) -> None:
        """Load all extracted offers from data folder."""
        self.offers = []
        scraped_data_folder = self.data_folder.parent / "rent_prices"

        for source_folder in self.data_folder.iterdir():
            if not source_folder.is_dir():
                continue

            source_name = source_folder.name

            for offer_file in source_folder.glob("*.json"):
                data = json.loads(offer_file.read_text(encoding="utf-8"))
                params = OfferParameters(**data)

                # Filter outliers
                if (
                    params.total_price < self.min_rent
                    or params.total_price > self.max_rent
                ):
                    continue
                if params.area is None or (
                    params.area < self.min_area or params.area > self.max_area
                ):
                    continue

                # Load URL from scraped data
                scraped_file = (
                    scraped_data_folder / source_name / offer_file.name
                )
                scraped_data = json.loads(
                    scraped_file.read_text(encoding="utf-8")
                )
                url = scraped_data["url"]

                cost_per_meter = (
                    params.total_price / params.area
                    if params.area and params.area > 0
                    else None
                )

                self.offers.append(
                    OfferResult(
                        source=source_name,
                        file_name=offer_file.name,
                        url=url,
                        parameters=params,
                        total_cost=params.total_price,
                        cost_per_meter=cost_per_meter,
                    )
                )

    @staticmethod
    def apply_filters(
        offers: list[OfferResult], filter_params: FilterParams
    ) -> list[OfferResult]:
        """Apply filters to offers list."""
        filtered = offers

        for filter_type in filter_params.filters:
            if filter_type == FilterType.INCLUDE_ONLY_STUDENTS:
                filtered = [
                    o for o in filtered if o.parameters.only_for_students
                ]
            elif filter_type == FilterType.EXCLUDE_ONLY_STUDENTS:
                filtered = [
                    o for o in filtered if not o.parameters.only_for_students
                ]
            elif filter_type == FilterType.INCLUDE_ONLY_WOMEN:
                filtered = [o for o in filtered if o.parameters.only_for_woman]
            elif filter_type == FilterType.EXCLUDE_ONLY_WOMEN:
                filtered = [
                    o for o in filtered if not o.parameters.only_for_woman
                ]
            elif filter_type == FilterType.INCLUDE_UTILITIES:
                filtered = [
                    o
                    for o in filtered
                    if o.parameters.utilities_included is True
                ]
            elif filter_type == FilterType.EXCLUDE_UTILITIES:
                filtered = [
                    o
                    for o in filtered
                    if o.parameters.utilities_included is False
                ]

        if filter_params.exclude_locations:
            filtered = [
                o
                for o in filtered
                if not any(
                    excluded.lower() in (o.parameters.location or "").lower()
                    or excluded.lower() in (o.parameters.address or "").lower()
                    for excluded in filter_params.exclude_locations
                )
            ]

        if filter_params.include_locations:
            filtered = [
                o
                for o in filtered
                if any(
                    included.lower() in (o.parameters.location or "").lower()
                    or included.lower() in (o.parameters.address or "").lower()
                    for included in filter_params.include_locations
                )
            ]

        if filter_params.exclude_offers:
            filtered = [
                o
                for o in filtered
                if o.file_name not in filter_params.exclude_offers
            ]

        return filtered

    def find_best(
        self,
        criteria: SearchCriteria,
        filter_params: FilterParams,
        top_n: int = 10,
    ) -> list[OfferResult]:
        """Find best offers based on criteria."""
        filtered_offers = self.apply_filters(self.offers, filter_params)

        if criteria == SearchCriteria.TOTAL_COST:
            sorted_offers = sorted(filtered_offers, key=lambda o: o.total_cost)
        elif criteria == SearchCriteria.COST_PER_METER:
            sorted_offers = sorted(
                [o for o in filtered_offers if o.cost_per_meter is not None],
                key=lambda o: o.cost_per_meter,
            )
        elif criteria == SearchCriteria.RENT_PRICE:
            sorted_offers = sorted(
                filtered_offers, key=lambda o: o.parameters.rent_price
            )
        elif criteria == SearchCriteria.DEPOSIT:
            sorted_offers = sorted(
                filtered_offers, key=lambda o: o.parameters.deposit
            )
        elif criteria == SearchCriteria.MINIMAL_RENT_DURATION:
            sorted_offers = sorted(
                filtered_offers,
                key=lambda o: o.parameters.minimal_rent_duration_months,
            )
        elif criteria == SearchCriteria.AREA:
            sorted_offers = sorted(
                [o for o in filtered_offers if o.parameters.area is not None],
                key=lambda o: o.parameters.area,
                reverse=True,
            )
        else:
            sorted_offers = filtered_offers

        return sorted_offers[:top_n]
