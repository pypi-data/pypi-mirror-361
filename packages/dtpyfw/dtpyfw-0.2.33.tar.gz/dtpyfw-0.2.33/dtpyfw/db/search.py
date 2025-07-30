from typing import Any
from math import ceil
from datetime import datetime
from sqlalchemy import func, or_, cast, and_, String, distinct as distinct_func
from sqlalchemy.orm import Session


__all__ = ("get_list",)


def convert_symbols_to_unicode(string: str):
    cleaned_string = ""
    for character in string:
        if ord(character) > 127:
            cleaned_string += "%"
        else:
            cleaned_string += character
    return cleaned_string


def make_condition(filter_item: dict, values: dict | list | str):
    columns = filter_item.get("columns")
    columns_logic = filter_item.get("columns_logic", "or")
    columns_type = filter_item.get("type", "select")
    is_json_column = filter_item.get("is_json", False)
    if is_json_column:
        columns_type = "search"

    logic_function = {
        "or": or_,
        "and": and_,
    }.get(columns_logic)

    if columns_type == "search":
        if is_json_column:
            filter_value = [convert_symbols_to_unicode(w) for w in values]
            return logic_function(
                *[
                    or_(
                        *[
                            func.lower(cast(column, String)).like(
                                func.lower(f'%"{x}"%')
                            )
                            for x in filter_value
                        ]
                    )
                    for column in columns
                ]
            )
        else:
            filter_value = "".join([c for c in values if ord(c) <= 127])
            return logic_function(
                *[
                    func.lower(cast(column, String)).like(
                        func.lower(f"%{filter_value}%")
                    )
                    for column in columns
                ]
            )
    elif columns_type == "select":
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
    elif columns_type == "number":
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
    elif columns_type == "date":
        value_min: datetime = values.get("min")
        value_max: datetime = values.get("max")

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
    else:
        return None


def get_list(
    current_query: dict,
    db: Session,
    model: Any,
    joins: list[dict] = None,
    pre_conditions: list = None,
    filters: list = None,
    options: list = None,
    distinct=None,
    primary_column: str = "id",
    get_function_parameters: dict = None,
    return_available_filters: bool = True,
    return_selected_filters: bool = True,
    export_mode: bool = False,
):
    if joins is None:
        joins = []

    if filters is None:
        filters = []

    page = current_query.get("page") or 1
    items_per_page = current_query.get("items_per_page") or 30

    if pre_conditions is None:
        pre_conditions = []

    if options is None:
        options = []

    if get_function_parameters is None:
        get_function_parameters = {}

    # Create Initial Model Query
    main_query = db.query(model)

    if distinct is True:
        count_query = db.query(
            func.count(distinct_func(getattr(model, primary_column)))
        )
    elif distinct:
        count_query = db.query(func.count(distinct_func(distinct)))
    else:
        count_query = db.query(func.count(getattr(model, primary_column)))

    for join_item in joins:
        main_query = main_query.join(**join_item)
        count_query = count_query.join(**join_item)

    main_query = main_query.filter(*pre_conditions)
    count_query = count_query.filter(*pre_conditions)

    # Initialize rows and conditions
    conditions = []

    names_conditions = {}
    for filter_item in filters:
        names_conditions[filter_item.get("name")] = []

    for filter_item in filters:
        name = filter_item.get("name")
        columns = filter_item.get("columns")
        values = current_query.get(name)
        if not columns or not name or not values:
            continue

        target_condition = make_condition(filter_item=filter_item, values=values)
        if target_condition is not None:
            conditions.append(target_condition)
            for inner_name, inner_name_values in names_conditions.items():
                if inner_name != name:
                    inner_name_values.append(target_condition)

    if conditions:
        main_query = main_query.filter(*conditions)
        count_query = count_query.filter(*conditions)

    if distinct is True:
        main_query = main_query.distinct()
    elif distinct:
        main_query = main_query.distinct(distinct)

    if options:
        main_query = main_query.options(*options)

    if sorting := (current_query.get("sorting") or []):
        order_by_list = []
        for item in sorting:
            sort_by = item.get("sort_by")
            if not sort_by:
                continue

            if hasattr(sort_by, "value"):
                sort_by = sort_by.value

            order_by = item.get("order_by")
            if not order_by:
                continue

            if hasattr(order_by, "value"):
                order_by = order_by.value

            order_by_list.append(getattr(getattr(model, sort_by), order_by)())

        final_query = main_query.order_by(*order_by_list)
    else:
        final_query = main_query

    if items_per_page and page:
        final_query = final_query.limit(items_per_page).offset(
            (page - 1) * items_per_page
        )

    rows = list(map(lambda x: x.get(**get_function_parameters), final_query.all()))

    if export_mode:
        return rows
    else:
        count = count_query.first()[0]
        current_query["total_row"] = count

        # Calculate pagination-related information
        if items_per_page and page:
            last_page = ceil(count / items_per_page)
            current_query["last_page"] = last_page
            current_query["has_next"] = last_page > page
            current_query["page"] = page
            current_query["items_per_page"] = items_per_page

        result = {
            "rows_data": rows,
            "payload": current_query,
        }

        if return_available_filters:
            from .search_filter_values import get_filters_value
            result['available_filters'] = get_filters_value(
                db=db,
                pre_conditions=pre_conditions,
                joins=joins,
                filters=filters,
                names_conditions=names_conditions,
            ) if filters is not None else []

        if return_selected_filters:
            from .search_selected_filters import make_selected_filters
            result['selected_filters'] = make_selected_filters(
                current_query=current_query,
                filters=filters,
            )

        # Return a dictionary containing the filter/sort options, current query data, and rows of data
        return result
