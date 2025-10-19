from __future__ import annotations

from enum import Enum


class SortDirection(str, Enum):
    """Sort direction enum."""

    ASC = "ASC"
    DESC = "DESC"


class SortField(str, Enum):
    """Sort field enum."""

    PRICE = "PRICE"
    DATE = "DATE"
    AREA = "AREA"
    CREATED_AT = "CREATED_AT"
