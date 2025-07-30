from typing import Optional

from pypika.functions import Function
from pypika.queries import Selectable
from pypika.terms import Criterion, Term
from typing_extensions import Literal

from tesseract_olap.exceptions.query import TimeScaleUnavailable
from tesseract_olap.query import (
    DataQuery,
    HierarchyField,
    LevelField,
    Restriction,
    TimeConstraint,
    TimeScale,
)

from .dialect import ClickHouseQuery, ToYYYYMMDD


def find_timerestriction(
    query: DataQuery,
) -> Optional[tuple[HierarchyField, LevelField, TimeConstraint]]:
    """Return the TimeRestriction object in a query, if defined.

    Also, if the type of requested restriction is COMPLETE, generates an extra
    column to be added to tfrom.
    """
    for hiefi in query.fields_qualitative:
        for lvlfi in hiefi.levels:
            if lvlfi.time_restriction is None:
                continue
            return (hiefi, lvlfi, lvlfi.time_restriction.constraint)
    return None


def make_date_column(
    hiefi: HierarchyField,
    query: DataQuery,
    tfrom: Selectable,
) -> Optional[Term]:
    time_format = hiefi.dimension.fkey_time_format
    fkey_column = hiefi.deepest_level.id_column(query.locale)
    field_name = f"lv_{fkey_column.hash}" if not hiefi.table else f"fk_{hiefi.alias}"
    field_fkey = tfrom.field(field_name)

    if time_format == "YYYYMMDD":
        return Function("YYYYMMDDToDate", field_fkey, alias="fk_datetime")

    if time_format == "YYYYMM":
        return Function("YYYYMMDDToDate", field_fkey * 100 + 1, alias="fk_datetime")

    if time_format in ("YYYYQ", "YYYYQQ", "YYYY-Q", "YYYY-QQ"):
        # parses the quarter into approximately the day at the half of the period
        # SQL is index-1
        index_q = 1 + time_format.index("Q") + (1 if "QQ" in time_format else 0)
        return Function(
            "makeDate",  # makeDate(year, dayOfYear)
            Function("toInt32", Function("substring", field_fkey, 1, 4)),
            (Function("toInt32", Function("substring", field_fkey, index_q, 1)) - 1) * 91 + 45,
            alias="fk_datetime",
        )

    return None


SQL_for_continuous_dates = """
WITH date_range AS (
    SELECT toDate('2023-01-01') + number AS date
    FROM numbers(365)  -- Adjust the range as needed
)
SELECT
    date_range.date,
    sum(transactions.amount) AS total_amount
FROM date_range
LEFT JOIN transactions ON date_range.date = toDate(transactions.date)
GROUP BY date_range.date
ORDER BY date_range.date
"""

SQL_for_highest_complete_year = """
SELECT
    toYear(date) AS year,
    sum(value) AS total_value
FROM transactions
WHERE toYear(date) < (
    SELECT max(toYear(date))
    FROM transactions
    GROUP BY toYear(date)
    HAVING count(distinct toMonth(date)) = 12
)
GROUP BY year
ORDER BY year
"""


def qb_timerel_yyyymmdd(
    query: DataQuery,
    tfrom: Selectable,
    hiefi: HierarchyField,
    lvlfi: LevelField,
    constr: tuple[Literal[Restriction.LEADING, Restriction.TRAILING], int],
) -> Criterion:
    """Create a Criterion for LEADING/TRAILING restrictions on YYYYMMDD columns."""
    fkey_column = hiefi.deepest_level.id_column(query.locale)
    field_name = f"lv_{fkey_column.hash}" if not hiefi.table else f"fk_{hiefi.alias}"
    field_fkey = tfrom.field(field_name)

    direction, amount = constr
    qb_limit = ClickHouseQuery.from_(tfrom)
    dir_function = "max" if direction is Restriction.TRAILING else "min"
    field_limit = Function("YYYYMMDDToDate", Function(dir_function, field_fkey))
    time_scale = lvlfi.time_scale

    if time_scale is TimeScale.YEAR:
        field_limit = Function("toStartOfYear", field_limit)
        if direction is Restriction.TRAILING:
            field_since = ToYYYYMMDD(Function("subtractYears", field_limit, amount - 1))
            return field_fkey >= qb_limit.select(field_since)

        field_until = ToYYYYMMDD(Function("addYears", field_limit, amount))
        return field_fkey < qb_limit.select(field_until)

    if time_scale is TimeScale.QUARTER:
        field_limit = Function("toStartOfQuarter", field_limit)
        if direction is Restriction.TRAILING:
            field_since = ToYYYYMMDD(Function("subtractQuarters", field_limit, amount - 1))
            return field_fkey >= qb_limit.select(field_since)

        field_until = ToYYYYMMDD(Function("addQuarters", field_limit, amount))
        return field_fkey < qb_limit.select(field_until)

    if time_scale is TimeScale.MONTH:
        field_limit = Function("toStartOfMonth", field_limit)
        if direction is Restriction.TRAILING:
            field_since = ToYYYYMMDD(Function("subtractMonths", field_limit, amount - 1))
            return field_fkey >= qb_limit.select(field_since)

        field_until = ToYYYYMMDD(Function("addMonths", field_limit, amount))
        return field_fkey < qb_limit.select(field_until)

    if time_scale is TimeScale.WEEK:
        field_limit = Function("toStartOfWeek", field_limit)
        if direction is Restriction.TRAILING:
            field_since = ToYYYYMMDD(Function("subtractWeeks", field_limit, amount - 1))
            return field_fkey >= qb_limit.select(field_since)

        field_until = ToYYYYMMDD(Function("addWeeks", field_limit, amount))
        return field_fkey < qb_limit.select(field_until)

    if time_scale is TimeScale.DAY:
        if direction is Restriction.TRAILING:
            field_since = ToYYYYMMDD(Function("subtractDays", field_limit, amount - 1))
            return field_fkey >= qb_limit.select(field_since)

        field_until = ToYYYYMMDD(Function("addDays", field_limit, amount))
        return field_fkey < qb_limit.select(field_until)

    raise TimeScaleUnavailable(query.cube.name, time_scale.value)


def qb_timerel_yyyymm(
    query: DataQuery,
    tfrom: Selectable,
    hiefi: HierarchyField,
    lvlfi: LevelField,
    constr: tuple[Literal[Restriction.LEADING, Restriction.TRAILING], int],
) -> Criterion:
    """Create a Criterion for LEADING/TRAILING restrictions on YYYYMM columns."""
    fkey_column = hiefi.deepest_level.id_column(query.locale)
    field_name = f"lv_{fkey_column.hash}" if not hiefi.table else f"fk_{hiefi.alias}"
    field_fkey = tfrom.field(field_name)

    direction, amount = constr
    qb_limit = ClickHouseQuery.from_(tfrom)
    dir_function = "max" if constr[0] is Restriction.TRAILING else "min"
    field_limit = Function("YYYYMMDDToDate", Function(dir_function, field_fkey) * 100 + 1)
    time_scale = lvlfi.time_scale

    if time_scale is TimeScale.YEAR:
        field_limit = Function("toStartOfYear", field_limit)
        if direction is Restriction.TRAILING:
            field_since = ToYYYYMMDD(Function("subtractYears", field_limit, amount - 1))
            return field_fkey >= qb_limit.select(Function("intDiv", field_since, 100))

        field_until = ToYYYYMMDD(Function("addYears", field_limit, amount))
        return field_fkey < qb_limit.select(Function("intDiv", field_until, 100))

    if time_scale is TimeScale.QUARTER:
        field_limit = Function("toStartOfQuarter", field_limit)
        if direction is Restriction.TRAILING:
            field_since = ToYYYYMMDD(Function("subtractQuarters", field_limit, amount - 1))
            return field_fkey >= qb_limit.select(Function("intDiv", field_since, 100))

        field_until = ToYYYYMMDD(Function("addQuarters", field_limit, amount))
        return field_fkey < qb_limit.select(Function("intDiv", field_until, 100))

    if time_scale is TimeScale.MONTH:
        if direction is Restriction.TRAILING:
            field_since = ToYYYYMMDD(Function("subtractMonths", field_limit, amount - 1))
            return field_fkey >= qb_limit.select(Function("intDiv", field_since, 100))

        field_until = ToYYYYMMDD(Function("addMonths", field_limit, amount))
        return field_fkey < qb_limit.select(Function("intDiv", field_until, 100))

    raise TimeScaleUnavailable(query.cube.name, time_scale.value)


def qb_timerel_yyyy(
    query: DataQuery,
    tfrom: Selectable,
    hiefi: HierarchyField,
    lvlfi: LevelField,
    constr: tuple[Literal[Restriction.LEADING, Restriction.TRAILING], int],
) -> Criterion:
    """Create a Criterion for LEADING/TRAILING restrictions on YYYY columns."""
    fkey_column = hiefi.deepest_level.id_column(query.locale)
    field_name = f"lv_{fkey_column.hash}" if not hiefi.table else f"fk_{hiefi.alias}"
    field_fkey = tfrom.field(field_name)

    direction, amount = constr
    qb_limit = ClickHouseQuery.from_(tfrom)
    dir_function = "max" if constr[0] is Restriction.TRAILING else "min"
    field_limit = Function(dir_function, field_fkey)
    time_scale = lvlfi.time_scale

    if time_scale is TimeScale.YEAR:
        if direction is Restriction.TRAILING:
            field_since = field_limit - (amount - 1)
            return field_fkey >= qb_limit.select(field_since)

        field_until = field_limit + amount
        return field_fkey < qb_limit.select(field_until)

    raise TimeScaleUnavailable(query.cube.name, time_scale.name)
