from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field
from pydantic import NonNegativeFloat
from pydantic import NonNegativeInt
from pydantic import PositiveFloat


class OfferParameters(BaseModel):
    """Discovered parameters from a rental offer."""

    rent_price: PositiveFloat = Field(description="Monthly rent price")
    other_prices: NonNegativeFloat = Field(
        default=0, description="Sum of administration rent cleaning etc"
    )
    area: float | None = Field(
        description="Area in square meters. Remember that it should be a room size and not area of the entire apartment"
    )
    rooms: int | None = Field(description="Number of rooms")
    address: str | None = Field(description="Full address of the property")
    location: str | None = Field(description="Location/neighborhood/district")
    floor: int | None = Field(description="Floor number")
    total_floors: int | None = Field(description="Total floors in building")
    available_from: str | None = Field(description="Availability date")
    utilities_included: bool | None = Field(
        description="Whether utilities are included in price"
    )
    deposit: NonNegativeFloat = Field(0, description="Security deposit amount")
    furnished: bool = Field(True, description="Whether furnished")
    only_for_woman: bool = Field(
        False, description="Whether the offer is only for woman"
    )
    only_for_students: bool = Field(
        False, description="Whether the offer is only for students"
    )
    minimal_rent_duration_months: NonNegativeInt = Field(
        0, description="Minimal duration of rent"
    )

    @property
    def total_price(self) -> float:
        return self.rent_price + self.other_prices
