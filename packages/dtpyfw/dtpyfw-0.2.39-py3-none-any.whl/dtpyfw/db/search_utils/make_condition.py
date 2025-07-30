from datetime import datetime
from typing import Any

from sqlalchemy import or_, and_, func, literal, Text, cast

__all__ = ("make_condition",)



def select_condition_maker(filter_item: dict, values: list):
    columns              = filter_item.get("columns", [])
    columns_logic        = filter_item.get("columns_logic", "or")
    case_insensitive     = filter_item.get("case_insensitive", False)
    use_similarity       = filter_item.get("use_similarity", False)
    similarity_threshold = filter_item.get("similarity_threshold", 0.3)
    logic_fn             = {"or": or_, "and": and_}[columns_logic]

    # Pre-process literals
    processed_values = [
        v.lower()
        if case_insensitive and isinstance(v, str)
        else v
        for v in values
    ]

    conditions = []

    if use_similarity:
        # Fuzzy‐match via trigram similarity for text columns
        for col in columns:
            for v in processed_values:
                if isinstance(v, str):
                    # cast column and literal to Text
                    lit_q = literal(v).cast(Text)
                    col_text = cast(col, Text)
                    # compare similarity to threshold
                    conditions.append(func.similarity(col_text, lit_q) >= similarity_threshold)
                else:
                    # non‐text types fall back to equality
                    conditions.append(col == v)
    else:
        # Exact‐match branch
        for col in columns:
            if case_insensitive and hasattr(col.type, 'python_type') and col.type.python_type is str:
                conditions.append(func.lower(col).in_(processed_values))
            else:
                conditions.append(col.in_(processed_values))

    return logic_fn(*conditions)


def number_condition_maker(filter_item: dict, values: dict):
    columns = filter_item.get("columns")
    columns_logic = filter_item.get("columns_logic", "or")
    logic_function = {
        "or": or_,
        "and": and_,
    }.get(columns_logic)

    value_min = values.get("min")
    value_max = values.get("max")
    if value_min is not None and value_max is not None:
        return logic_function(
            *[
                getattr(column, "between")(value_min, value_max)
                for column in columns
            ]
        )
    elif value_min is None and value_max is not None:
        return logic_function(*[column <= value_max for column in columns])
    elif value_min is not None and value_max is None:
        return logic_function(*[column >= value_min for column in columns])


def date_condition_maker(filter_item: dict, values: dict):
    value_min: datetime = values.get("min")
    value_max: datetime = values.get("max")

    columns = filter_item.get("columns")
    columns_logic = filter_item.get("columns_logic", "or")
    logic_function = {
        "or": or_,
        "and": and_,
    }.get(columns_logic)

    if value_min is not None and value_max is not None:
        return logic_function(
            *[
                getattr(column, "between")(value_min, value_max)
                for column in columns
            ]
        )
    elif value_min is None and value_max is not None:
        return logic_function(
            *[or_(column <= value_max, column == None) for column in columns]
        )
    elif value_min is not None and value_max is None:
        return logic_function(*[column >= value_min for column in columns])


def make_condition(filter_item: dict, values: Any):
    columns_type = filter_item.get("type", "select")

    if columns_type == "select":
        return select_condition_maker(
            filter_item=filter_item,
            values=values,
        )
    elif columns_type == "number":
        return number_condition_maker(
            filter_item=filter_item,
            values=values,
        )
    elif columns_type == "date":
        return date_condition_maker(
            filter_item=filter_item,
            values=values,
        )
    else:
        return None
