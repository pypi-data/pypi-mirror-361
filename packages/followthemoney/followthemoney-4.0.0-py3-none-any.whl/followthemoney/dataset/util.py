from normality import slugify
from typing import Annotated, Any
from pydantic import BeforeValidator

from followthemoney.types import registry


def dataset_name_check(value: str) -> str:
    """Check that the given value is a valid dataset name. This doesn't convert
    or clean invalid names, but raises an error if they are not compliant to
    force the user to fix an invalid name"""
    if slugify(value, sep="_") != value:
        raise ValueError("Invalid %s: %r" % ("dataset name", value))
    return value


def type_check_date(value: Any) -> str:
    """Check that the given value is a valid date string."""
    cleaned = registry.date.clean(value)
    if cleaned is None:
        raise ValueError("Invalid date: %r" % value)
    return cleaned


PartialDate = Annotated[str, BeforeValidator(type_check_date)]


def type_check_country(value: Any) -> str:
    """Check that the given value is a valid country code."""
    cleaned = registry.country.clean(value)
    if cleaned is None:
        raise ValueError("Invalid country code: %r" % value)
    return cleaned


CountryCode = Annotated[str, BeforeValidator(type_check_country)]


class Named:
    name: str

    def __init__(self, name: str) -> None:
        self.name = name

    def __eq__(self, other: Any) -> bool:
        try:
            return not not self.name == other.name
        except AttributeError:
            return False

    def __lt__(self, other: Any) -> bool:
        return self.name.__lt__(other.name)

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.name!r})>"
