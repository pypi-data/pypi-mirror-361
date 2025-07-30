"""Universal Query Adapter Package.

This package provides a unified interface for querying both SQL and NoSQL databases
through a single, consistent API.
"""

from acb.adapters.query._base import (
    QueryBase,
    QueryBaseSettings,
    UniversalQuery,
    UniversalQueryProtocol,
)
from acb.adapters.query.nosql import NoSqlQueryAdapter, NoSqlQuerySettings
from acb.adapters.query.sql import SqlQueryAdapter, SqlQuerySettings
from acb.adapters.query.universal import UniversalQueryAdapter, UniversalQuerySettings

__all__ = [
    "NoSqlQueryAdapter",
    "NoSqlQuerySettings",
    "QueryBase",
    "QueryBaseSettings",
    "SqlQueryAdapter",
    "SqlQuerySettings",
    "UniversalQuery",
    "UniversalQueryAdapter",
    "UniversalQueryProtocol",
    "UniversalQuerySettings",
]
