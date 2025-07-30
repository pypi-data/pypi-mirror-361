"""SQL Query Adapter Implementation.

This module implements the universal query interface for SQL databases,
bridging the gap between the universal query protocol and SQL-specific operations.
"""

from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from acb.adapters.query._base import (
    QueryBase,
    QueryBaseSettings,
    UniversalQueryProtocol,
)
from acb.adapters.sql._base import SqlBase


class SqlQuerySettings(QueryBaseSettings):
    sql_adapter: str = "postgresql"
    enable_orm: bool = True
    auto_commit: bool = True


class SqlQueryAdapter(QueryBase, UniversalQueryProtocol):
    def __init__(self, settings: SqlQuerySettings) -> None:
        super().__init__(settings)
        self.settings = settings
        self._sql_adapter: SqlBase | None = None
        self._metadata_cache: dict[str, Any] = {}

    async def _ensure_sql_adapter(self) -> SqlBase:
        if self._sql_adapter is None:
            from acb.adapters import import_adapter

            SqlAdapter = import_adapter("sql")
            self._sql_adapter = SqlAdapter()
        return self._sql_adapter

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
        adapter = await self._ensure_sql_adapter()

        if isinstance(data, list):
            return await self._insert_many(adapter, table, data, **kwargs)
        return await self._insert_one(adapter, table, data, **kwargs)

    async def _insert_one(
        self,
        adapter: SqlBase,
        table: str,
        data: dict[str, Any],
        **kwargs,
    ) -> Any:
        async with adapter.get_session() as session:
            try:
                columns = ", ".join(data.keys())
                placeholders = ", ".join(f":{key}" for key in data)
                query = text(
                    f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) RETURNING *",
                )

                result = await session.execute(query, data)
                if self.settings.auto_commit:
                    await session.commit()

                return result.fetchone()
            except Exception:
                await session.rollback()
                raise

    async def _insert_many(
        self,
        adapter: SqlBase,
        table: str,
        data: list[dict[str, Any]],
        **kwargs,
    ) -> Any:
        async with adapter.get_session() as session:
            try:
                if not data:
                    return []

                columns = ", ".join(data[0].keys())
                placeholders = ", ".join(f":{key}" for key in data[0])
                query = text(
                    f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) RETURNING *",
                )

                results = []
                for record in data:
                    result = await session.execute(query, record)
                    results.append(result.fetchone())

                if self.settings.auto_commit:
                    await session.commit()

                return results
            except Exception:
                await session.rollback()
                raise

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
        adapter = await self._ensure_sql_adapter()

        async with adapter.get_session() as session:
            select_fields = kwargs.get("select", ["*"])
            if isinstance(select_fields, list) and select_fields:
                if select_fields == ["*"]:
                    query = f"SELECT * FROM {table}"
                else:
                    query = f"SELECT {', '.join(select_fields)} FROM {table}"
            else:
                query = f"SELECT * FROM {table}"

            params = {}
            if filter:
                conditions = []
                for key, value in filter.items():
                    if isinstance(value, dict):
                        for op, val in value.items():
                            sql_op = self._convert_operator(op)
                            param_name = f"{key}_{len(params)}"
                            conditions.append(f"{key} {sql_op} :{param_name}")
                            params[param_name] = val
                    else:
                        param_name = f"{key}_{len(params)}"
                        conditions.append(f"{key} = :{param_name}")
                        params[param_name] = value

                if conditions:
                    query += f" WHERE {' AND '.join(conditions)}"

            order_by = kwargs.get("order_by", [])
            if order_by:
                query += f" ORDER BY {', '.join(order_by)}"

            limit = kwargs.get("limit")
            offset = kwargs.get("offset")
            if limit is not None:
                query += f" LIMIT {limit}"
            if offset is not None:
                query += f" OFFSET {offset}"

            result = await session.execute(text(query), params)
            rows = result.fetchall()

            return [dict(row._mapping) for row in rows]

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
        adapter = await self._ensure_sql_adapter()

        async with adapter.get_session() as session:
            try:
                set_clauses = []
                params = {}

                for key, value in data.items():
                    param_name = f"set_{key}"
                    set_clauses.append(f"{key} = :{param_name}")
                    params[param_name] = value

                query = f"UPDATE {table} SET {', '.join(set_clauses)}"

                if filter:
                    conditions = []
                    for key, value in filter.items():
                        param_name = f"where_{key}"
                        conditions.append(f"{key} = :{param_name}")
                        params[param_name] = value

                    if conditions:
                        query += f" WHERE {' AND '.join(conditions)}"

                query += " RETURNING *"

                result = await session.execute(text(query), params)
                if self.settings.auto_commit:
                    await session.commit()

                return result.fetchall()
            except Exception:
                await session.rollback()
                raise

    async def delete(self, table: str, filter: dict[str, Any], **kwargs) -> Any:
        return await self._delete(table, filter, **kwargs)

    async def _delete(self, table: str, filter: dict[str, Any], **kwargs) -> Any:
        adapter = await self._ensure_sql_adapter()
        async with adapter.get_session() as session:
            try:
                query = f"DELETE FROM {table}"
                params = {}
                if filter:
                    conditions = []
                    for key, value in filter.items():
                        param_name = f"where_{key}"
                        conditions.append(f"{key} = :{param_name}")
                        params[param_name] = value
                    if conditions:
                        query += f" WHERE {' AND '.join(conditions)}"
                query += " RETURNING *"
                result = await session.execute(text(query), params)
                if self.settings.auto_commit:
                    await session.commit()

                return result.fetchall()
            except Exception:
                await session.rollback()
                raise

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
        adapter = await self._ensure_sql_adapter()

        async with adapter.get_session() as session:
            query = f"SELECT COUNT(*) FROM {table}"
            params = {}

            if filter:
                conditions = []
                for key, value in filter.items():
                    param_name = f"where_{key}"
                    conditions.append(f"{key} = :{param_name}")
                    params[param_name] = value

                if conditions:
                    query += f" WHERE {' AND '.join(conditions)}"

            result = await session.execute(text(query), params)
            return result.scalar() or 0

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
        adapter = await self._ensure_sql_adapter()

        async with adapter.get_session() as session:
            query = self._build_aggregation_query(table, pipeline)

            result = await session.execute(text(query))
            rows = result.fetchall()

            return [dict(row._mapping) for row in rows]

    def _build_aggregation_query(
        self,
        table: str,
        pipeline: list[dict[str, Any]],
    ) -> str:
        return self._convert_pipeline_to_sql(table, pipeline)

    def _convert_pipeline_to_sql(
        self,
        table: str,
        pipeline: list[dict[str, Any]],
    ) -> str:
        query_parts = {
            "select": ["*"],
            "from": table,
            "where": [],
            "group_by": [],
            "order_by": [],
            "limit": None,
        }

        for stage in pipeline:
            if "$match" in stage:
                query_parts["where"].extend(
                    self._convert_match_to_where(stage["$match"]),
                )
            elif "$group" in stage:
                query_parts.update(self._convert_group_to_sql(stage["$group"]))
            elif "$sort" in stage:
                query_parts["order_by"].extend(
                    self._convert_sort_to_order(stage["$sort"]),
                )
            elif "$limit" in stage:
                query_parts["limit"] = stage["$limit"]

        return self._build_sql_from_parts(query_parts)

    def _convert_match_to_where(self, match_conditions: dict[str, Any]) -> list[str]:
        conditions = []
        for key, value in match_conditions.items():
            conditions.append(f"{key} = '{value}'")
        return conditions

    def _convert_group_to_sql(self, group_stage: dict[str, Any]) -> dict[str, Any]:
        parts = {"select": [], "group_by": []}
        group_by = group_stage.get("_id", "")
        if group_by:
            parts["select"].append(group_by)
            parts["group_by"].append(group_by)
            for key, value in group_stage.items():
                if key != "_id" and isinstance(value, dict):
                    for agg_op, field in value.items():
                        if agg_op == "$sum":
                            parts["select"].append(f"SUM({field}) as {key}")
                        elif agg_op == "$avg":
                            parts["select"].append(f"AVG({field}) as {key}")
                        elif agg_op == "$count":
                            parts["select"].append(f"COUNT(*) as {key}")

        return parts

    def _convert_sort_to_order(self, sort_stage: dict[str, Any]) -> list[str]:
        order_clauses = []
        for key, direction in sort_stage.items():
            order_clauses.append(f"{key} {'ASC' if direction == 1 else 'DESC'}")
        return order_clauses

    def _build_sql_from_parts(self, parts: dict[str, Any]) -> str:
        query = f"SELECT {', '.join(parts['select'])} FROM {parts['from']}"
        if parts["where"]:
            query += f" WHERE {' AND '.join(parts['where'])}"
        if parts["group_by"]:
            query += f" GROUP BY {', '.join(parts['group_by'])}"
        if parts["order_by"]:
            query += f" ORDER BY {', '.join(parts['order_by'])}"
        if parts["limit"]:
            query += f" LIMIT {parts['limit']}"

        return query

    @asynccontextmanager
    async def transaction(self) -> AbstractAsyncContextManager[AsyncSession]:
        adapter = await self._ensure_sql_adapter()
        async with adapter.get_session() as session, session.begin():
            yield session

    def _convert_operator(self, op: str) -> str:
        operator_map = {
            "$gt": ">",
            "$gte": ">=",
            "$lt": "<",
            "$lte": "<=",
            "$ne": "!=",
            "$eq": "=",
            "$in": "IN",
            "$nin": "NOT IN",
            "$like": "LIKE",
            "$ilike": "ILIKE",
        }
        return operator_map.get(op, "=")

    async def _create_adapter(self, adapter_type: str) -> UniversalQueryProtocol:
        if adapter_type == "sql":
            return self
        msg = f"Unsupported adapter type: {adapter_type}"
        raise ValueError(msg)
