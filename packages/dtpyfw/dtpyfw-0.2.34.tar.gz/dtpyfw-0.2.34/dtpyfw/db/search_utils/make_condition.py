from datetime import datetime
from typing import Any

from sqlalchemy import or_, and_

__all__ = ("make_condition",)


def convert_symbols_to_unicode(string: str):
    cleaned_string = ""
    for character in string:
        if ord(character) > 127:
            cleaned_string += "%"
        else:
            cleaned_string += character
    return cleaned_string


def select_condition_maker(filter_item: dict, values: list):
    columns = filter_item.get("columns")
    columns_logic = filter_item.get("columns_logic", "or")
    logic_function = {
        "or": or_,
        "and": and_,
    }.get(columns_logic)

    return logic_function(
        *[
            getattr(column, "in_")(
                [
                    (
                        convert_symbols_to_unicode(element)
                        if isinstance(element, str)
                        else element
                    )
                    for element in values
                ]
            )
            for column in columns
        ]
    )


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
