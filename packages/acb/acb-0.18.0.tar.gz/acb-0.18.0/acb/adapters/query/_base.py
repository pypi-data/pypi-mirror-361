"""Universal Query Adapter Base Module.

This module provides a universal query interface that works with both SQL and NoSQL databases,
following the ACB adapter pattern with public/private method delegation.
"""

import asyncio
from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Any, Protocol

from acb.config import AdapterBase, Settings


class UniversalQueryProtocol(Protocol):
    async def create(
        self,
        table: str,
        data: dict[str, Any] | list[dict[str, Any]],
        **kwargs,
    ) -> Any: ...

    async def read(
        self,
        table: str,
        filter: dict[str, Any] | None = None,
        **kwargs,
    ) -> list[dict[str, Any]]: ...

    async def update(
        self,
        table: str,
        filter: dict[str, Any],
        data: dict[str, Any],
        **kwargs,
    ) -> Any: ...

    async def delete(self, table: str, filter: dict[str, Any], **kwargs) -> Any: ...

    async def count(
        self,
        table: str,
        filter: dict[str, Any] | None = None,
        **kwargs,
    ) -> int: ...

    async def exists(self, table: str, filter: dict[str, Any], **kwargs) -> bool: ...

    async def aggregate(
        self,
        table: str,
        pipeline: list[dict[str, Any]],
        **kwargs,
    ) -> list[dict[str, Any]]: ...

    async def transaction(self) -> AbstractAsyncContextManager[Any]: ...


class QueryBaseSettings(Settings):
    default_adapter: str = "sql"
    table_routing: dict[str, str] = {}
    enable_caching: bool = True
    query_timeout: int = 30


class UniversalQuery:
    def __init__(self, adapter: UniversalQueryProtocol, table: str) -> None:
        self.adapter = adapter
        self.table = table
        self._filter: dict[str, Any] = {}
        self._limit: int | None = None
        self._offset: int | None = None
        self._order: list[str] = []
        self._select: list[str] = []

    def where(self, **conditions) -> "UniversalQuery":
        self._filter.update(conditions)
        return self

    def filter(self, filter_dict: dict[str, Any]) -> "UniversalQuery":
        self._filter.update(filter_dict)
        return self

    def limit(self, n: int) -> "UniversalQuery":
        self._limit = n
        return self

    def offset(self, n: int) -> "UniversalQuery":
        self._offset = n
        return self

    def order_by(self, *fields: str) -> "UniversalQuery":
        self._order.extend(fields)
        return self

    def select(self, *fields: str) -> "UniversalQuery":
        self._select.extend(fields)
        return self

    async def all(self) -> list[dict[str, Any]]:
        return await self.adapter.read(
            self.table,
            self._filter,
            limit=self._limit,
            offset=self._offset,
            order_by=self._order,
            select=self._select,
        )

    async def first(self) -> dict[str, Any] | None:
        results = await self.adapter.read(
            self.table,
            self._filter,
            limit=1,
            order_by=self._order,
            select=self._select,
        )
        return results[0] if results else None

    async def count(self) -> int:
        return await self.adapter.count(self.table, self._filter)

    async def exists(self) -> bool:
        return await self.adapter.exists(self.table, self._filter)

    async def update(self, data: dict[str, Any]) -> Any:
        return await self.adapter.update(self.table, self._filter, data)

    async def delete(self) -> Any:
        return await self.adapter.delete(self.table, self._filter)


class QueryBase(AdapterBase, ABC):
    def __init__(self, settings: QueryBaseSettings) -> None:
        super().__init__()
        self.settings = settings
        self._adapters: dict[str, UniversalQueryProtocol] = {}
        self._adapter_lock = asyncio.Lock()

    async def query(self, table: str) -> UniversalQuery:
        return await self._query(table)

    async def _query(self, table: str) -> UniversalQuery:
        adapter = await self._get_adapter(table)
        return UniversalQuery(adapter, table)

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
        adapter = await self._get_adapter(table)
        return await adapter.create(table, data, **kwargs)

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
        adapter = await self._get_adapter(table)
        return await adapter.read(table, filter, **kwargs)

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
        adapter = await self._get_adapter(table)
        return await adapter.update(table, filter, data, **kwargs)

    async def delete(self, table: str, filter: dict[str, Any], **kwargs) -> Any:
        return await self._delete(table, filter, **kwargs)

    async def _delete(self, table: str, filter: dict[str, Any], **kwargs) -> Any:
        adapter = await self._get_adapter(table)
        return await adapter.delete(table, filter, **kwargs)

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
        adapter = await self._get_adapter(table)
        return await adapter.count(table, filter, **kwargs)

    async def exists(self, table: str, filter: dict[str, Any], **kwargs) -> bool:
        return await self._exists(table, filter, **kwargs)

    async def _exists(self, table: str, filter: dict[str, Any], **kwargs) -> bool:
        adapter = await self._get_adapter(table)
        return await adapter.exists(table, filter, **kwargs)

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
        adapter = await self._get_adapter(table)
        return await adapter.aggregate(table, pipeline, **kwargs)

    @asynccontextmanager
    async def transaction(
        self,
        table: str | None = None,
    ) -> AbstractAsyncContextManager[Any]:
        if table:
            adapter = await self._get_adapter(table)
            async with adapter.transaction() as txn:
                yield txn
        else:
            async with self._transaction() as txn:
                yield txn

    @asynccontextmanager
    async def _transaction(self) -> AbstractAsyncContextManager[Any]:
        yield None

    async def _get_adapter(self, table: str) -> UniversalQueryProtocol:
        adapter_type = self._determine_adapter_type(table)
        if adapter_type not in self._adapters:
            async with self._adapter_lock:
                if adapter_type not in self._adapters:
                    self._adapters[adapter_type] = await self._create_adapter(
                        adapter_type,
                    )

        return self._adapters[adapter_type]

    def _determine_adapter_type(self, table: str) -> str:
        return self.settings.table_routing.get(table, self.settings.default_adapter)

    @abstractmethod
    async def _create_adapter(self, adapter_type: str) -> UniversalQueryProtocol:
        pass
