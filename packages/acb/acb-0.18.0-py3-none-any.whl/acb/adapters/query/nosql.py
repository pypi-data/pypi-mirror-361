"""NoSQL Query Adapter Implementation.

This module implements the universal query interface for NoSQL databases,
bridging the gap between the universal query protocol and NoSQL-specific operations.
"""

from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Any

from acb.adapters.nosql._base import NosqlBase
from acb.adapters.query._base import (
    QueryBase,
    QueryBaseSettings,
    UniversalQueryProtocol,
)


class NoSqlQuerySettings(QueryBaseSettings):
    nosql_adapter: str = "mongodb"
    collection_prefix: str = ""
    enable_indexing: bool = True
    batch_size: int = 1000


class NoSqlQueryAdapter(QueryBase, UniversalQueryProtocol):
    def __init__(self, settings: NoSqlQuerySettings) -> None:
        super().__init__(settings)
        self.settings = settings
        self._nosql_adapter: NosqlBase | None = None
        self._collection_cache: dict[str, Any] = {}

    async def _ensure_nosql_adapter(self) -> NosqlBase:
        if self._nosql_adapter is None:
            from acb.adapters import import_adapter

            NosqlAdapter = import_adapter("nosql")
            self._nosql_adapter = NosqlAdapter()
        return self._nosql_adapter

    def _get_collection_name(self, table: str) -> str:
        if self.settings.collection_prefix:
            return f"{self.settings.collection_prefix}{table}"
        return table

    async def create(
        self,
        table: str,
        data: dict[str, Any] | list[dict[str, Any]],
        **kwargs,
    ) -> Any:
        return await self._create(table, data, **kwargs)

    async def _create(
        self,
        table: str,
        data: dict[str, Any] | list[dict[str, Any]],
        **kwargs,
    ) -> Any:
        adapter = await self._ensure_nosql_adapter()
        collection = self._get_collection_name(table)

        if isinstance(data, list):
            return await adapter.insert_many(collection, data, **kwargs)
        return await adapter.insert_one(collection, data, **kwargs)

    async def read(
        self,
        table: str,
        filter: dict[str, Any] | None = None,
        **kwargs,
    ) -> list[dict[str, Any]]:
        return await self._read(table, filter, **kwargs)

    async def _read(
        self,
        table: str,
        filter: dict[str, Any] | None = None,
        **kwargs,
    ) -> list[dict[str, Any]]:
        adapter = await self._ensure_nosql_adapter()
        collection = self._get_collection_name(table)

        limit = kwargs.get("limit")
        offset = kwargs.get("offset")

        select_fields = kwargs.get("select")
        projection = {}
        if select_fields and select_fields != ["*"]:
            projection = dict.fromkeys(select_fields, 1)

        sort_fields = kwargs.get("order_by", [])
        sort_spec = []
        for field in sort_fields:
            if field.startswith("-"):
                sort_spec.append((field[1:], -1))
            else:
                sort_spec.append((field, 1))

        query_options = {}
        if limit is not None:
            query_options["limit"] = limit
        if offset is not None:
            query_options["skip"] = offset
        if projection:
            query_options["projection"] = projection
        if sort_spec:
            query_options["sort"] = sort_spec

        if filter is None:
            filter = {}

        converted_filter = self._convert_query_filter(filter)

        results = await adapter.find(collection, converted_filter, **query_options)

        return [self._normalize_document(doc) for doc in results]

    async def update(
        self,
        table: str,
        filter: dict[str, Any],
        data: dict[str, Any],
        **kwargs,
    ) -> Any:
        return await self._update(table, filter, data, **kwargs)

    async def _update(
        self,
        table: str,
        filter: dict[str, Any],
        data: dict[str, Any],
        **kwargs,
    ) -> Any:
        adapter = await self._ensure_nosql_adapter()
        collection = self._get_collection_name(table)

        update_doc = {"$set": data}

        update_many = kwargs.get("update_many", False)

        converted_filter = self._convert_query_filter(filter)

        if update_many:
            return await adapter.update_many(
                collection,
                converted_filter,
                update_doc,
                **kwargs,
            )
        return await adapter.update_one(
            collection,
            converted_filter,
            update_doc,
            **kwargs,
        )

    async def delete(self, table: str, filter: dict[str, Any], **kwargs) -> Any:
        return await self._delete(table, filter, **kwargs)

    async def _delete(self, table: str, filter: dict[str, Any], **kwargs) -> Any:
        adapter = await self._ensure_nosql_adapter()
        collection = self._get_collection_name(table)
        delete_many = kwargs.get("delete_many", False)
        converted_filter = self._convert_query_filter(filter)
        if delete_many:
            return await adapter.delete_many(collection, converted_filter, **kwargs)
        return await adapter.delete_one(collection, converted_filter, **kwargs)

    async def count(
        self,
        table: str,
        filter: dict[str, Any] | None = None,
        **kwargs,
    ) -> int:
        return await self._count(table, filter, **kwargs)

    async def _count(
        self,
        table: str,
        filter: dict[str, Any] | None = None,
        **kwargs,
    ) -> int:
        adapter = await self._ensure_nosql_adapter()
        collection = self._get_collection_name(table)

        if filter is None:
            filter = {}

        converted_filter = self._convert_query_filter(filter)
        return await adapter.count(collection, converted_filter, **kwargs)

    async def exists(self, table: str, filter: dict[str, Any], **kwargs) -> bool:
        return await self._exists(table, filter, **kwargs)

    async def _exists(self, table: str, filter: dict[str, Any], **kwargs) -> bool:
        count = await self.count(table, filter, **kwargs)
        return count > 0

    async def aggregate(
        self,
        table: str,
        pipeline: list[dict[str, Any]],
        **kwargs,
    ) -> list[dict[str, Any]]:
        return await self._aggregate(table, pipeline, **kwargs)

    async def _aggregate(
        self,
        table: str,
        pipeline: list[dict[str, Any]],
        **kwargs,
    ) -> list[dict[str, Any]]:
        adapter = await self._ensure_nosql_adapter()
        collection = self._get_collection_name(table)

        results = await adapter.aggregate(collection, pipeline, **kwargs)

        return [self._normalize_document(doc) for doc in results]

    @asynccontextmanager
    async def transaction(self) -> AbstractAsyncContextManager[Any]:
        adapter = await self._ensure_nosql_adapter()
        if hasattr(adapter, "transaction"):
            async with adapter.transaction() as txn:
                yield txn
        else:
            yield None

    def _convert_query_filter(self, filter: dict[str, Any]) -> dict[str, Any]:
        converted = {}
        for key, value in filter.items():
            if isinstance(value, dict):
                converted[key] = self._convert_operators(value)
            elif key.startswith("$"):
                converted[key] = value
            else:
                converted[key] = value

        return converted

    def _convert_operators(self, operators: dict[str, Any]) -> dict[str, Any]:
        converted = {}
        for op, value in operators.items():
            if op.startswith("$"):
                converted[op] = value
            else:
                operator_map = {
                    "gt": "$gt",
                    "gte": "$gte",
                    "lt": "$lt",
                    "lte": "$lte",
                    "ne": "$ne",
                    "eq": "$eq",
                    "in": "$in",
                    "nin": "$nin",
                    "regex": "$regex",
                    "exists": "$exists",
                }
                nosql_op = operator_map.get(op, f"${op}")
                converted[nosql_op] = value

        return converted

    def _normalize_document(self, doc: dict[str, Any]) -> dict[str, Any]:
        normalized = doc.copy()
        if "_id" in normalized:
            id_value = normalized["_id"]
            if hasattr(id_value, "__str__"):
                normalized["_id"] = str(id_value)
        for key, value in normalized.items():
            if hasattr(value, "__str__") and not isinstance(
                value,
                str | int | float | bool | list | dict,
            ):
                normalized[key] = str(value)

        return normalized

    async def _create_adapter(self, adapter_type: str) -> UniversalQueryProtocol:
        if adapter_type == "nosql":
            return self
        msg = f"Unsupported adapter type: {adapter_type}"
        raise ValueError(msg)

    async def batch_create(
        self,
        table: str,
        data: list[dict[str, Any]],
        batch_size: int | None = None,
    ) -> list[Any]:
        if batch_size is None:
            batch_size = self.settings.batch_size

        results = []
        for i in range(0, len(data), batch_size):
            batch = data[i : i + batch_size]
            batch_result = await self.create(table, batch)
            results.extend(
                batch_result if isinstance(batch_result, list) else [batch_result],
            )

        return results

    async def bulk_update(self, table: str, updates: list[dict[str, Any]]) -> list[Any]:
        adapter = await self._ensure_nosql_adapter()
        collection = self._get_collection_name(table)
        if hasattr(adapter, "bulk_write"):
            operations = []
            for update in updates:
                filter_doc = update.get("filter", {})
                update_doc = update.get("update", {})
                operations.append(
                    {
                        "update_one": {
                            "filter": self._convert_query_filter(filter_doc),
                            "update": {"$set": update_doc},
                        },
                    },
                )

            return await adapter.bulk_write(collection, operations)
        results = []
        for update in updates:
            filter_doc = update.get("filter", {})
            update_doc = update.get("update", {})
            result = await self.update(table, filter_doc, update_doc)
            results.append(result)

        return results
