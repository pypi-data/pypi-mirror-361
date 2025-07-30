from sqlalchemy import func, or_, cast, String, literal, desc, Text, ColumnElement, UnaryExpression
from sqlalchemy.dialects.postgresql import REGCONFIG


def free_search(searchable_columns: list, search_query: str, search_similarity_threshold: float) -> tuple[list[ColumnElement], list[UnaryExpression]]:
    lang = literal('english', type_=REGCONFIG)
    concat = func.concat_ws(" ", *[col.cast(String) for col in searchable_columns])
    search_vector = func.to_tsvector(lang, concat)

    ts_query = func.websearch_to_tsquery('english', search_query)
    rank = func.ts_rank_cd(search_vector, ts_query)
    lit_q = literal(search_query).cast(Text)

    sim_cols = [
        func.similarity(cast(col, Text), lit_q)
        for col in searchable_columns
    ]

    best_sim = func.greatest(*sim_cols)

    combined_score = func.greatest(rank, best_sim)

    conditions = [
        or_(
            search_vector.op("@@")(ts_query),
            best_sim > search_similarity_threshold
        )
    ]

    sort_by = [desc(combined_score)]

    return conditions, sort_by
