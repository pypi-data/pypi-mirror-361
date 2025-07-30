from datetime import date, datetime
from typing import Optional

from deltalake.table import FilterLiteralType

from dagster_delta.io_manager.base import (
    DELTA_DATE_FORMAT,
    DELTA_DATETIME_FORMAT,
)


def create_predicate(
    partition_filters: list[FilterLiteralType],
    target_alias: Optional[str] = None,
) -> str:
    partition_predicates = []
    for part_filter in partition_filters:
        column = f"{target_alias}.{part_filter[0]}" if target_alias is not None else part_filter[0]
        value = part_filter[2]
        if isinstance(value, (int, float, bool)):
            value = str(value)
        elif isinstance(value, str):
            value = f"'{value}'"
        elif isinstance(value, list):
            value = str(tuple(v for v in value))
        elif isinstance(value, date):
            value = f"'{value.strftime(DELTA_DATE_FORMAT)}'"
        elif isinstance(value, datetime):
            value = f"'{value.strftime(DELTA_DATETIME_FORMAT)}'"
        partition_predicates.append(f"{column} {part_filter[1]} {value}")

    return " AND ".join(partition_predicates)
