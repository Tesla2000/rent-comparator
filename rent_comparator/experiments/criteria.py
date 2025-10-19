from __future__ import annotations

from enum import Enum

from pydantic import BaseModel
from pydantic import model_validator


class SearchCriteria(str, Enum):
    """Criteria for finding best rental offers."""

    TOTAL_COST = "total_cost"
    COST_PER_METER = "cost_per_meter"
    RENT_PRICE = "rent_price"
    DEPOSIT = "deposit"
    MINIMAL_RENT_DURATION = "minimal_rent_duration"
    AREA = "area"


class FilterType(str, Enum):
    """Filter types for excluding offers."""

    INCLUDE_ONLY_STUDENTS = "include_only_students"
    EXCLUDE_ONLY_STUDENTS = "exclude_only_students"
    INCLUDE_ONLY_WOMEN = "include_only_women"
    EXCLUDE_ONLY_WOMEN = "exclude_only_women"
    INCLUDE_UTILITIES = "include_utilities"
    EXCLUDE_UTILITIES = "exclude_utilities"


class FilterParams(BaseModel):
    """Parameters for filtering offers."""

    filters: list[FilterType] = []
    exclude_locations: list[str] | None = None
    include_locations: list[str] | None = None
    exclude_offers: dict[str, str] = {}

    @model_validator(mode="after")
    def validate_location_filters(self) -> FilterParams:
        """Ensure include_locations and exclude_locations are not both provided."""
        if self.include_locations and self.exclude_locations:
            raise ValueError(
                "Cannot specify both include_locations and exclude_locations"
            )
        return self
