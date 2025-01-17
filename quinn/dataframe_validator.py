import copy
from typing import List

from pyspark.sql import DataFrame
from pyspark.sql.types import StructType


class DataFrameMissingColumnError(ValueError):
    """raise this when there's a DataFrame column error"""


class DataFrameMissingStructFieldError(ValueError):
    """raise this when there's a DataFrame column error"""


class DataFrameProhibitedColumnError(ValueError):
    """raise this when a DataFrame includes prohibited columns"""


def validate_presence_of_columns(df: DataFrame, required_col_names: List[str]) -> None:
    all_col_names = df.columns
    missing_col_names = [x for x in required_col_names if x not in all_col_names]
    error_message = "The {missing_col_names} columns are not included in the DataFrame with the following columns {all_col_names}".format(
        missing_col_names=missing_col_names, all_col_names=all_col_names
    )
    if missing_col_names:
        raise DataFrameMissingColumnError(error_message)


def validate_schema(df: DataFrame, required_schema: StructType, ignore_nullable: bool=False) -> None:
    _all_struct_fields = copy.deepcopy(df.schema)
    _required_schema = copy.deepcopy(required_schema)

    if ignore_nullable:
        for x in _all_struct_fields:
            x.nullable = None

        for x in _required_schema:
            x.nullable = None

    missing_struct_fields = [x for x in _required_schema if x not in _all_struct_fields]
    error_message = "The {missing_struct_fields} StructFields are not included in the DataFrame with the following StructFields {all_struct_fields}".format(
        missing_struct_fields=missing_struct_fields,
        all_struct_fields=_all_struct_fields,
    )
    if missing_struct_fields:
        raise DataFrameMissingStructFieldError(error_message)


def validate_absence_of_columns(df: DataFrame, prohibited_col_names: List[str]) -> None:
    all_col_names = df.columns
    extra_col_names = [x for x in all_col_names if x in prohibited_col_names]
    error_message = "The {extra_col_names} columns are not allowed to be included in the DataFrame with the following columns {all_col_names}".format(
        extra_col_names=extra_col_names, all_col_names=all_col_names
    )
    if extra_col_names:
        raise DataFrameProhibitedColumnError(error_message)
