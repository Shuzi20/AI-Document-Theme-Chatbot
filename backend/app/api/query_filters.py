# File: backend/app/api/query_filters.py

from qdrant_client.models import Filter, FieldCondition, MatchValue, Range

def build_query_filter(excluded_docs=None, doc_type=None, date_after=None, date_before=None):
    must = []
    must_not = []

    # ⛔ Exclude specific documents
    if excluded_docs:
        must_not.extend([
            FieldCondition(
                key="metadata.doc_name",
                match=MatchValue(value=doc.strip().lower())
            ) for doc in excluded_docs
        ])

    # ✅ Filter by document type
    if doc_type and doc_type.lower() != "all":
        must.append(
            FieldCondition(
                key="metadata.doc_type",
                match=MatchValue(value=doc_type.strip().lower())
            )
        )

    # ✅ Filter by date range
    if date_after or date_before:
        date_range = {}
        if date_after:
            date_range["gte"] = date_after
        if date_before:
            date_range["lte"] = date_before

        must.append(
            FieldCondition(
                key="metadata.uploaded_at",
                range=Range(**date_range)
            )
        )

    return Filter(must=must, must_not=must_not) if (must or must_not) else None
