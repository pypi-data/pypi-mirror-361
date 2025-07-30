"""Tests for Universal Query Adapter."""

from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from acb.adapters.query import (
    UniversalQuery,
    UniversalQueryAdapter,
    UniversalQuerySettings,
)


class MockSqlAdapter:
    """Mock SQL adapter for testing."""

    def __init__(self) -> None:
        self.settings = MagicMock()
        self.create = AsyncMock()
        self.read = AsyncMock()
        self.update = AsyncMock()
        self.delete = AsyncMock()
        self.count = AsyncMock()
        self.exists = AsyncMock()
        self.aggregate = AsyncMock()
        self._transaction_mock = AsyncMock()

    @asynccontextmanager
    async def transaction(self) -> AbstractAsyncContextManager[Any]:
        yield self._transaction_mock


class MockNoSqlAdapter:
    """Mock NoSQL adapter for testing."""

    def __init__(self) -> None:
        self.settings = MagicMock()
        self.create = AsyncMock()
        self.read = AsyncMock()
        self.update = AsyncMock()
        self.delete = AsyncMock()
        self.count = AsyncMock()
        self.exists = AsyncMock()
        self.aggregate = AsyncMock()
        self._transaction_mock = AsyncMock()

    @asynccontextmanager
    async def transaction(self) -> AbstractAsyncContextManager[Any]:
        yield self._transaction_mock


@pytest.fixture
def query_settings():
    """Create test settings."""
    return UniversalQuerySettings(
        default_adapter="sql",
        table_routing={
            "users": "sql",
            "posts": "sql",
            "logs": "nosql",
            "events": "nosql",
        },
        sql_table_patterns=["user_*", "product_*"],
        nosql_table_patterns=["log_*", "event_*"],
        auto_detect_type=True,
    )


@pytest.fixture
def universal_adapter(query_settings):
    """Create universal query adapter."""
    return UniversalQueryAdapter(query_settings)


@pytest.fixture
def mock_sql_adapter():
    """Create mock SQL adapter."""
    return MockSqlAdapter()


@pytest.fixture
def mock_nosql_adapter():
    """Create mock NoSQL adapter."""
    return MockNoSqlAdapter()


class TestUniversalQueryAdapter:
    """Test universal query adapter functionality."""

    @pytest.mark.asyncio
    async def test_adapter_routing_explicit(self, universal_adapter) -> None:
        """Test explicit table routing."""
        # Test SQL routing
        assert universal_adapter._determine_adapter_type("users") == "sql"
        assert universal_adapter._determine_adapter_type("posts") == "sql"

        # Test NoSQL routing
        assert universal_adapter._determine_adapter_type("logs") == "nosql"
        assert universal_adapter._determine_adapter_type("events") == "nosql"

    @pytest.mark.asyncio
    async def test_adapter_routing_patterns(self, universal_adapter) -> None:
        """Test pattern-based routing."""
        # Test SQL patterns
        assert universal_adapter._determine_adapter_type("user_profiles") == "sql"
        assert universal_adapter._determine_adapter_type("product_catalog") == "sql"

        # Test NoSQL patterns
        assert universal_adapter._determine_adapter_type("log_access") == "nosql"
        assert universal_adapter._determine_adapter_type("event_tracking") == "nosql"

    @pytest.mark.asyncio
    async def test_adapter_routing_default(self, universal_adapter) -> None:
        """Test default adapter routing."""
        # Unknown table should use default adapter
        assert universal_adapter._determine_adapter_type("unknown_table") == "sql"

    @pytest.mark.asyncio
    async def test_pattern_matching(self, universal_adapter) -> None:
        """Test pattern matching functionality."""
        # Test prefix patterns
        assert universal_adapter._match_pattern("user_profiles", "user_*")
        assert not universal_adapter._match_pattern("product_catalog", "user_*")

        # Test suffix patterns
        assert universal_adapter._match_pattern("access_log", "*_log")
        assert not universal_adapter._match_pattern("log_access", "*_log")

        # Test exact match
        assert universal_adapter._match_pattern("users", "users")
        assert not universal_adapter._match_pattern("user", "users")

    @pytest.mark.asyncio
    async def test_create_records(self, universal_adapter, mock_sql_adapter) -> None:
        """Test creating records."""
        with patch.object(
            universal_adapter,
            "_ensure_sql_adapter",
            return_value=mock_sql_adapter,
        ):
            mock_sql_adapter.create.return_value = {"id": 1, "name": "test"}

            result = await universal_adapter.create("users", {"name": "test"})

            mock_sql_adapter.create.assert_called_once_with("users", {"name": "test"})
            assert result == {"id": 1, "name": "test"}

    @pytest.mark.asyncio
    async def test_read_records(self, universal_adapter, mock_sql_adapter) -> None:
        """Test reading records."""
        with patch.object(
            universal_adapter,
            "_ensure_sql_adapter",
            return_value=mock_sql_adapter,
        ):
            mock_sql_adapter.read.return_value = [{"id": 1, "name": "test"}]

            result = await universal_adapter.read("users", {"name": "test"})

            mock_sql_adapter.read.assert_called_once_with("users", {"name": "test"})
            assert result == [{"id": 1, "name": "test"}]

    @pytest.mark.asyncio
    async def test_update_records(self, universal_adapter, mock_sql_adapter) -> None:
        """Test updating records."""
        with patch.object(
            universal_adapter,
            "_ensure_sql_adapter",
            return_value=mock_sql_adapter,
        ):
            mock_sql_adapter.update.return_value = {"id": 1, "name": "updated"}

            result = await universal_adapter.update(
                "users",
                {"id": 1},
                {"name": "updated"},
            )

            mock_sql_adapter.update.assert_called_once_with(
                "users",
                {"id": 1},
                {"name": "updated"},
            )
            assert result == {"id": 1, "name": "updated"}

    @pytest.mark.asyncio
    async def test_delete_records(self, universal_adapter, mock_sql_adapter) -> None:
        """Test deleting records."""
        with patch.object(
            universal_adapter,
            "_ensure_sql_adapter",
            return_value=mock_sql_adapter,
        ):
            mock_sql_adapter.delete.return_value = {"deleted": 1}

            result = await universal_adapter.delete("users", {"id": 1})

            mock_sql_adapter.delete.assert_called_once_with("users", {"id": 1})
            assert result == {"deleted": 1}

    @pytest.mark.asyncio
    async def test_count_records(self, universal_adapter, mock_sql_adapter) -> None:
        """Test counting records."""
        with patch.object(
            universal_adapter,
            "_ensure_sql_adapter",
            return_value=mock_sql_adapter,
        ):
            mock_sql_adapter.count.return_value = 5

            result = await universal_adapter.count("users", {"active": True})

            mock_sql_adapter.count.assert_called_once_with("users", {"active": True})
            assert result == 5

    @pytest.mark.asyncio
    async def test_exists_records(self, universal_adapter, mock_sql_adapter) -> None:
        """Test checking if records exist."""
        with patch.object(
            universal_adapter,
            "_ensure_sql_adapter",
            return_value=mock_sql_adapter,
        ):
            mock_sql_adapter.exists.return_value = True

            result = await universal_adapter.exists(
                "users",
                {"email": "test@example.com"},
            )

            mock_sql_adapter.exists.assert_called_once_with(
                "users",
                {"email": "test@example.com"},
            )
            assert result

    @pytest.mark.asyncio
    async def test_aggregate_records(
        self, universal_adapter, mock_nosql_adapter
    ) -> None:
        """Test aggregating records."""
        with patch.object(
            universal_adapter,
            "_ensure_nosql_adapter",
            return_value=mock_nosql_adapter,
        ):
            pipeline = [{"$group": {"_id": "$category", "count": {"$sum": 1}}}]
            mock_nosql_adapter.aggregate.return_value = [{"_id": "tech", "count": 5}]

            result = await universal_adapter.aggregate("logs", pipeline)

            mock_nosql_adapter.aggregate.assert_called_once_with("logs", pipeline)
            assert result == [{"_id": "tech", "count": 5}]

    @pytest.mark.asyncio
    async def test_query_builder(self, universal_adapter, mock_sql_adapter) -> None:
        """Test query builder functionality."""
        with patch.object(
            universal_adapter,
            "_ensure_sql_adapter",
            return_value=mock_sql_adapter,
        ):
            mock_sql_adapter.read.return_value = [{"id": 1, "name": "test", "age": 25}]

            query = await universal_adapter.query("users")
            result = await query.where(age=25).limit(10).order_by("name").all()

            mock_sql_adapter.read.assert_called_once_with(
                "users",
                {"age": 25},
                limit=10,
                offset=None,
                order_by=["name"],
                select=[],
            )
            assert result == [{"id": 1, "name": "test", "age": 25}]

    @pytest.mark.asyncio
    async def test_query_builder_first(
        self, universal_adapter, mock_sql_adapter
    ) -> None:
        """Test query builder first() method."""
        with patch.object(
            universal_adapter,
            "_ensure_sql_adapter",
            return_value=mock_sql_adapter,
        ):
            mock_sql_adapter.read.return_value = [{"id": 1, "name": "test"}]

            query = await universal_adapter.query("users")
            result = await query.where(id=1).first()

            mock_sql_adapter.read.assert_called_once_with(
                "users",
                {"id": 1},
                limit=1,
                order_by=[],
                select=[],
            )
            assert result == {"id": 1, "name": "test"}

    @pytest.mark.asyncio
    async def test_query_builder_first_empty(
        self, universal_adapter, mock_sql_adapter
    ) -> None:
        """Test query builder first() with no results."""
        with patch.object(
            universal_adapter,
            "_ensure_sql_adapter",
            return_value=mock_sql_adapter,
        ):
            mock_sql_adapter.read.return_value = []

            query = await universal_adapter.query("users")
            result = await query.where(id=999).first()

            assert result is None

    @pytest.mark.asyncio
    async def test_single_table_transaction(
        self, universal_adapter, mock_sql_adapter
    ) -> None:
        """Test single table transaction."""
        with patch.object(
            universal_adapter,
            "_ensure_sql_adapter",
            return_value=mock_sql_adapter,
        ):
            async with universal_adapter.transaction("users") as txn:
                assert txn is not None
                assert "default" in txn

    @pytest.mark.asyncio
    async def test_cross_db_query(
        self,
        universal_adapter,
        mock_sql_adapter,
        mock_nosql_adapter,
    ) -> None:
        """Test cross-database queries."""
        with (
            patch.object(
                universal_adapter,
                "_ensure_sql_adapter",
                return_value=mock_sql_adapter,
            ),
            patch.object(
                universal_adapter,
                "_ensure_nosql_adapter",
                return_value=mock_nosql_adapter,
            ),
        ):
            mock_sql_adapter.read.return_value = [{"id": 1, "name": "test"}]
            mock_nosql_adapter.read.return_value = [{"_id": "1", "event": "login"}]

            queries = [
                {"table": "users", "operation": "read", "filter": {"id": 1}},
                {"table": "logs", "operation": "read", "filter": {"user_id": 1}},
            ]

            result = await universal_adapter.cross_db_query(queries)

            assert "query_0" in result
            assert "query_1" in result
            mock_sql_adapter.read.assert_called_once()
            mock_nosql_adapter.read.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_table_sql(self, universal_adapter, mock_sql_adapter) -> None:
        """Test table analysis for SQL tables."""
        with patch.object(
            universal_adapter,
            "_ensure_sql_adapter",
            return_value=mock_sql_adapter,
        ):
            mock_sql_adapter.count.return_value = 100

            result = await universal_adapter.analyze_table("users")

            assert result["table"] == "users"
            assert result["adapter_type"] == "sql"
            assert result["record_count"] == 100
            assert "sql_info" in result
            assert result["sql_info"]["supports_transactions"]

    @pytest.mark.asyncio
    async def test_analyze_table_nosql(
        self, universal_adapter, mock_nosql_adapter
    ) -> None:
        """Test table analysis for NoSQL tables."""
        with patch.object(
            universal_adapter,
            "_ensure_nosql_adapter",
            return_value=mock_nosql_adapter,
        ):
            mock_nosql_adapter.count.return_value = 500

            result = await universal_adapter.analyze_table("logs")

            assert result["table"] == "logs"
            assert result["adapter_type"] == "nosql"
            assert result["record_count"] == 500
            assert "nosql_info" in result
            assert result["nosql_info"]["supports_aggregation"]


class TestUniversalQuery:
    """Test universal query builder."""

    def test_query_builder_chain(self) -> None:
        """Test query builder method chaining."""
        mock_adapter = AsyncMock()
        query = UniversalQuery(mock_adapter, "users")

        result = (
            query.where(name="test")
            .limit(10)
            .offset(5)
            .order_by("created_at")
            .select("id", "name")
        )

        assert result._filter == {"name": "test"}
        assert result._limit == 10
        assert result._offset == 5
        assert result._order == ["created_at"]
        assert result._select == ["id", "name"]

    def test_query_builder_filter(self) -> None:
        """Test query builder filter method."""
        mock_adapter = AsyncMock()
        query = UniversalQuery(mock_adapter, "users")

        result = query.filter({"age": 25, "active": True})

        assert result._filter == {"age": 25, "active": True}

    @pytest.mark.asyncio
    async def test_query_builder_count(self) -> None:
        """Test query builder count method."""
        mock_adapter = AsyncMock()
        mock_adapter.count.return_value = 5

        query = UniversalQuery(mock_adapter, "users")
        result = await query.where(active=True).count()

        mock_adapter.count.assert_called_once_with("users", {"active": True})
        assert result == 5

    @pytest.mark.asyncio
    async def test_query_builder_exists(self) -> None:
        """Test query builder exists method."""
        mock_adapter = AsyncMock()
        mock_adapter.exists.return_value = True

        query = UniversalQuery(mock_adapter, "users")
        result = await query.where(email="test@example.com").exists()

        mock_adapter.exists.assert_called_once_with(
            "users",
            {"email": "test@example.com"},
        )
        assert result

    @pytest.mark.asyncio
    async def test_query_builder_update(self) -> None:
        """Test query builder update method."""
        mock_adapter = AsyncMock()
        mock_adapter.update.return_value = {"updated": 1}

        query = UniversalQuery(mock_adapter, "users")
        result = await query.where(id=1).update({"name": "updated"})

        mock_adapter.update.assert_called_once_with(
            "users",
            {"id": 1},
            {"name": "updated"},
        )
        assert result == {"updated": 1}

    @pytest.mark.asyncio
    async def test_query_builder_delete(self) -> None:
        """Test query builder delete method."""
        mock_adapter = AsyncMock()
        mock_adapter.delete.return_value = {"deleted": 1}

        query = UniversalQuery(mock_adapter, "users")
        result = await query.where(id=1).delete()

        mock_adapter.delete.assert_called_once_with("users", {"id": 1})
        assert result == {"deleted": 1}


@pytest.mark.asyncio
async def test_adapter_caching(universal_adapter, mock_sql_adapter) -> None:
    """Test adapter instance caching."""
    with patch.object(
        universal_adapter,
        "_ensure_sql_adapter",
        return_value=mock_sql_adapter,
    ) as mock_ensure:
        # First call should create adapter
        await universal_adapter._get_adapter("users")
        assert mock_ensure.call_count == 1

        # Second call should use cached adapter
        await universal_adapter._get_adapter("users")
        assert mock_ensure.call_count == 1


@pytest.mark.asyncio
async def test_type_caching(universal_adapter) -> None:
    """Test adapter type caching."""
    # First call should determine type
    type1 = universal_adapter._determine_adapter_type("users")
    assert type1 == "sql"

    # Second call should use cached type
    type2 = universal_adapter._determine_adapter_type("users")
    assert type2 == "sql"

    # Cache should contain the result
    assert "users" in universal_adapter._type_cache
    assert universal_adapter._type_cache["users"] == "sql"
