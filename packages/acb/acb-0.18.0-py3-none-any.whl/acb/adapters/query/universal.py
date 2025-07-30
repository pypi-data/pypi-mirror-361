"""Universal Query Adapter Implementation.

This module provides a unified interface that can work with both SQL and NoSQL databases
based on configuration and table routing.
"""

import asyncio
from contextlib import AbstractAsyncContextManager, asynccontextmanager, suppress
from typing import Any

from acb.adapters.query._base import (
    QueryBase,
    QueryBaseSettings,
    UniversalQueryProtocol,
)
from acb.adapters.query.nosql import NoSqlQueryAdapter, NoSqlQuerySettings
from acb.adapters.query.sql import SqlQueryAdapter, SqlQuerySettings


class UniversalQuerySettings(QueryBaseSettings):
    sql_adapter: str = "postgresql"
    sql_enable_orm: bool = True
    sql_auto_commit: bool = True

    nosql_adapter: str = "mongodb"
    nosql_collection_prefix: str = ""
    nosql_enable_indexing: bool = True
    nosql_batch_size: int = 1000

    auto_detect_type: bool = True
    sql_table_patterns: list[str] = []
    nosql_table_patterns: list[str] = []

    enable_cross_db_transactions: bool = False
    enable_query_caching: bool = True
    cache_ttl: int = 300


class UniversalQueryAdapter(QueryBase):
    def __init__(self, settings: UniversalQuerySettings) -> None:
        super().__init__(settings)
        self.settings = settings
        self._sql_adapter: SqlQueryAdapter | None = None
        self._nosql_adapter: NoSqlQueryAdapter | None = None
        self._adapter_cache: dict[str, UniversalQueryProtocol] = {}
        self._type_cache: dict[str, str] = {}

    async def _ensure_sql_adapter(self) -> SqlQueryAdapter:
        if self._sql_adapter is None:
            sql_settings = SqlQuerySettings(
                sql_adapter=self.settings.sql_adapter,
                enable_orm=self.settings.sql_enable_orm,
                auto_commit=self.settings.sql_auto_commit,
                table_routing=self.settings.table_routing,
                enable_caching=self.settings.enable_caching,
                query_timeout=self.settings.query_timeout,
            )
            self._sql_adapter = SqlQueryAdapter(sql_settings)
        return self._sql_adapter

    async def _ensure_nosql_adapter(self) -> NoSqlQueryAdapter:
        if self._nosql_adapter is None:
            nosql_settings = NoSqlQuerySettings(
                nosql_adapter=self.settings.nosql_adapter,
                collection_prefix=self.settings.nosql_collection_prefix,
                enable_indexing=self.settings.nosql_enable_indexing,
                batch_size=self.settings.nosql_batch_size,
                table_routing=self.settings.table_routing,
                enable_caching=self.settings.enable_caching,
                query_timeout=self.settings.query_timeout,
            )
            self._nosql_adapter = NoSqlQueryAdapter(nosql_settings)
        return self._nosql_adapter

    async def _create_adapter(self, adapter_type: str) -> UniversalQueryProtocol:
        if adapter_type == "sql":
            return await self._ensure_sql_adapter()
        if adapter_type == "nosql":
            return await self._ensure_nosql_adapter()
        msg = f"Unsupported adapter type: {adapter_type}"
        raise ValueError(msg)

    def _determine_adapter_type(self, table: str) -> str:
        if table in self._type_cache:
            return self._type_cache[table]
        if table in self.settings.table_routing:
            adapter_type = self.settings.table_routing[table]
            self._type_cache[table] = adapter_type
            return adapter_type
        if self.settings.auto_detect_type:
            for pattern in self.settings.sql_table_patterns:
                if self._match_pattern(table, pattern):
                    self._type_cache[table] = "sql"
                    return "sql"
            for pattern in self.settings.nosql_table_patterns:
                if self._match_pattern(table, pattern):
                    self._type_cache[table] = "nosql"
                    return "nosql"
        adapter_type = self.settings.default_adapter
        self._type_cache[table] = adapter_type
        return adapter_type

    def _match_pattern(self, table: str, pattern: str) -> bool:
        if "*" in pattern:
            import fnmatch

            return fnmatch.fnmatch(table, pattern)
        if pattern.startswith("*"):
            return table.endswith(pattern[1:])
        if pattern.endswith("*"):
            return table.startswith(pattern[:-1])
        return table == pattern

    async def create(
        self,
        table: str,
        data: dict[str, Any] | list[dict[str, Any]],
        **kwargs,
    ) -> Any:
        return await self._create(table, data, **kwargs)

    async def read(
        self,
        table: str,
        filter: dict[str, Any] | None = None,
        **kwargs,
    ) -> list[dict[str, Any]]:
        return await self._read(table, filter, **kwargs)

    async def update(
        self,
        table: str,
        filter: dict[str, Any],
        data: dict[str, Any],
        **kwargs,
    ) -> Any:
        return await self._update(table, filter, data, **kwargs)

    async def delete(self, table: str, filter: dict[str, Any], **kwargs) -> Any:
        return await self._delete(table, filter, **kwargs)

    async def count(
        self,
        table: str,
        filter: dict[str, Any] | None = None,
        **kwargs,
    ) -> int:
        return await self._count(table, filter, **kwargs)

    async def exists(self, table: str, filter: dict[str, Any], **kwargs) -> bool:
        return await self._exists(table, filter, **kwargs)

    async def aggregate(
        self,
        table: str,
        pipeline: list[dict[str, Any]],
        **kwargs,
    ) -> list[dict[str, Any]]:
        return await self._aggregate(table, pipeline, **kwargs)

    @asynccontextmanager
    async def transaction(
        self,
        *tables: str,
    ) -> AbstractAsyncContextManager[dict[str, Any]]:
        if not tables:
            async with self._transaction() as txn:
                yield txn
        elif len(tables) == 1:
            adapter = await self._get_adapter(tables[0])
            async with adapter.transaction() as txn:
                yield {"default": txn}
        elif self.settings.enable_cross_db_transactions:
            async with self._cross_db_transaction(tables) as txn:
                yield txn
        else:
            async with self._multi_table_transaction(tables) as txn:
                yield txn

    @asynccontextmanager
    async def _cross_db_transaction(
        self,
        tables: list[str],
    ) -> AbstractAsyncContextManager[dict[str, Any]]:
        adapter_tables = {}
        for table in tables:
            adapter_type = self._determine_adapter_type(table)
            if adapter_type not in adapter_tables:
                adapter_tables[adapter_type] = []
            adapter_tables[adapter_type].append(table)

        transactions = {}
        try:
            for adapter_type in adapter_tables:
                adapter = await self._create_adapter(adapter_type)
                txn = await adapter.transaction().__aenter__()
                transactions[adapter_type] = txn

            yield transactions

            for adapter_type, txn in transactions.items():
                await txn.__aexit__(None, None, None)
        except Exception as e:
            for adapter_type, txn in transactions.items():
                with suppress(Exception):
                    await txn.__aexit__(type(e), e, e.__traceback__)
            raise

    @asynccontextmanager
    async def _multi_table_transaction(
        self,
        tables: list[str],
    ) -> AbstractAsyncContextManager[dict[str, Any]]:
        adapter_tables = {}
        for table in tables:
            adapter_type = self._determine_adapter_type(table)
            if adapter_type not in adapter_tables:
                adapter_tables[adapter_type] = []
            adapter_tables[adapter_type].append(table)

        transactions = {}
        for adapter_type in adapter_tables:
            adapter = await self._create_adapter(adapter_type)
            transactions[adapter_type] = adapter.transaction()

        active_txns = {}
        try:
            for adapter_type, txn_ctx in transactions.items():
                txn = await txn_ctx.__aenter__()
                active_txns[adapter_type] = (txn_ctx, txn)

            yield {k: v[1] for k, v in active_txns.items()}

            for adapter_type, (txn_ctx, txn) in active_txns.items():
                await txn_ctx.__aexit__(None, None, None)
        except Exception as e:
            for adapter_type, (txn_ctx, txn) in active_txns.items():
                with suppress(Exception):
                    await txn_ctx.__aexit__(type(e), e, e.__traceback__)
            raise

    async def cross_db_query(self, queries: list[dict[str, Any]]) -> dict[str, Any]:
        results = {}
        grouped_queries = {}
        for i, query in enumerate(queries):
            table = query.get("table")
            if not table:
                continue
            adapter_type = self._determine_adapter_type(table)
            if adapter_type not in grouped_queries:
                grouped_queries[adapter_type] = []
            grouped_queries[adapter_type].append((i, query))
        tasks = []
        for adapter_type, adapter_queries in grouped_queries.items():
            task = asyncio.create_task(
                self._execute_adapter_queries(adapter_type, adapter_queries),
            )
            tasks.append(task)
        adapter_results = await asyncio.gather(*tasks, return_exceptions=True)
        for adapter_result in adapter_results:
            if isinstance(adapter_result, Exception):
                raise adapter_result
            results.update(adapter_result)

        return results

    async def _execute_adapter_queries(
        self,
        adapter_type: str,
        queries: list[tuple[int, dict[str, Any]]],
    ) -> dict[str, Any]:
        adapter = await self._create_adapter(adapter_type)
        results = {}

        for query_id, query in queries:
            operation = query.get("operation", "read")
            table = query["table"]

            if operation == "read":
                result = await adapter.read(
                    table,
                    query.get("filter"),
                    **query.get("options", {}),
                )
            elif operation == "create":
                result = await adapter.create(
                    table,
                    query["data"],
                    **query.get("options", {}),
                )
            elif operation == "update":
                result = await adapter.update(
                    table,
                    query["filter"],
                    query["data"],
                    **query.get("options", {}),
                )
            elif operation == "delete":
                result = await adapter.delete(
                    table,
                    query["filter"],
                    **query.get("options", {}),
                )
            elif operation == "count":
                result = await adapter.count(
                    table,
                    query.get("filter"),
                    **query.get("options", {}),
                )
            elif operation == "aggregate":
                result = await adapter.aggregate(
                    table,
                    query["pipeline"],
                    **query.get("options", {}),
                )
            else:
                msg = f"Unsupported operation: {operation}"
                raise ValueError(msg)

            results[f"query_{query_id}"] = result

        return results

    async def analyze_table(self, table: str) -> dict[str, Any]:
        adapter = await self._get_adapter(table)
        adapter_type = self._determine_adapter_type(table)
        analysis = {
            "table": table,
            "adapter_type": adapter_type,
            "record_count": await adapter.count(table),
            "adapter_info": {
                "type": adapter_type,
                "settings": adapter.settings.model_dump()
                if hasattr(adapter.settings, "model_dump")
                else str(adapter.settings),
            },
        }
        if adapter_type == "sql":
            analysis["sql_info"] = {
                "supports_transactions": True,
                "supports_joins": True,
                "supports_indexes": True,
            }
        elif adapter_type == "nosql":
            analysis["nosql_info"] = {
                "supports_transactions": hasattr(adapter, "transaction"),
                "supports_aggregation": True,
                "supports_indexes": True,
            }

        return analysis
