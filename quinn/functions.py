import re
from numbers import Number
from typing import Any, Callable, List, Optional

import pyspark.sql.functions as F
from pyspark.sql import Column
from pyspark.sql.types import *


def single_space(col: Column) -> Column:
    return F.trim(F.regexp_replace(col, " +", " "))


def remove_all_whitespace(col: Column) -> Column:
    return F.regexp_replace(col, "\\s+", "")


def anti_trim(col: Column) -> Column:
    return F.regexp_replace(col, "\\b\\s+\\b", "")


def remove_non_word_characters(col: Column) -> Column:
    return F.regexp_replace(col, "[^\\w\\s]+", "")


def exists(f: Callable[[Any], bool]):
    def temp_udf(l):
        return any(map(f, l))

    return F.udf(temp_udf, BooleanType())


def forall(f: Callable[[Any], bool]):
    def temp_udf(l):
        return all(map(f, l))

    return F.udf(temp_udf, BooleanType())


def multi_equals(value: Any):
    def temp_udf(*cols):
        return all(map(lambda col: col == value, cols))

    return F.udf(temp_udf, BooleanType())


def week_start_date(col: Column, week_start_day: str = "Sun") -> Column:
    _raise_if_invalid_day(week_start_day)
    # the "standard week" in Spark is from Sunday to Saturday
    mapping = {
        "Sun": "Sat",
        "Mon": "Sun",
        "Tue": "Mon",
        "Wed": "Tue",
        "Thu": "Wed",
        "Fri": "Thu",
        "Sat": "Fri",
    }
    end = week_end_date(col, mapping[week_start_day])
    return F.date_add(end, -6)


def week_end_date(col: Column, week_end_day: str = "Sat") -> Column:
    _raise_if_invalid_day(week_end_day)
    # these are the default Spark mappings.  Spark considers Sunday the first day of the week.
    day_of_week_mapping = {
        "Sun": 1,
        "Mon": 2,
        "Tue": 3,
        "Wed": 4,
        "Thu": 5,
        "Fri": 6,
        "Sat": 7,
    }
    return F.when(
        F.dayofweek(col).eqNullSafe(F.lit(day_of_week_mapping[week_end_day])), col
    ).otherwise(F.next_day(col, week_end_day))


def _raise_if_invalid_day(day: str) -> None:
    valid_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    if day not in valid_days:
        message = "The day you entered '{0}' is not valid.  Here are the valid days: [{1}]".format(
            day, ",".join(valid_days)
        )
        raise ValueError(message)


def approx_equal(col1: Column, col2: Column, threshhold: Number) -> Column:
    return F.abs(col1 - col2) < threshhold


def array_choice(col: Column) -> Column:
    index = (F.rand() * F.size(col)).cast("int")
    return col[index]


@F.udf(returnType=ArrayType(StringType()))
def regexp_extract_all(s: str, regexp: str) -> Optional[List[re.Match]]:
    return None if s == None else re.findall(regexp, s)
