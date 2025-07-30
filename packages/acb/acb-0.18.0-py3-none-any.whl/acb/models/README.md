# Universal Query Interface

ACB's Universal Query Interface provides a database and model agnostic approach to data access, enabling you to write queries that work consistently across SQL and NoSQL databases while maintaining full type safety and supporting multiple query patterns.

## Table of Contents

- [Overview](#overview)
- [Core Concepts](#core-concepts)
- [Query Patterns](#query-patterns)
  - [Simple Query Style](#simple-query-style)
  - [Repository Pattern](#repository-pattern)
  - [Specification Pattern](#specification-pattern)
  - [Advanced Query Builder](#advanced-query-builder)
  - [Hybrid Query Interface](#hybrid-query-interface)
- [Model Adapters](#model-adapters)
  - [SQLModel Adapter](#sqlmodel-adapter)
  - [Pydantic Adapter](#pydantic-adapter)
- [Database Adapters](#database-adapters)
  - [SQL Database Adapter](#sql-database-adapter)
  - [NoSQL Database Adapter](#nosql-database-adapter)
- [Configuration](#configuration)
- [Best Practices](#best-practices)
- [Examples](#examples)
- [API Reference](#api-reference)

## Overview

The Universal Query Interface solves the problem of vendor lock-in and code duplication when working with different database technologies. Instead of learning different query syntaxes for SQL and NoSQL databases, you can use a single, consistent interface that adapts to your chosen database and model frameworks.

### Key Features

- **Database Agnostic**: Works with SQL (MySQL, PostgreSQL, SQLite) and NoSQL (MongoDB, Firestore, Redis)
- **Model Agnostic**: Supports SQLModel, Pydantic, and any Python class
- **Type Safety**: Full generic type support with Python's type system
- **Multiple Query Styles**: Choose the right abstraction level for your use case
- **Composable Specifications**: Build complex business rules with reusable components
- **Automatic Caching**: Built-in caching support at the repository level
- **Transaction Support**: Consistent transaction handling across all databases

## Core Concepts

### Protocol-Based Design

The Universal Query Interface uses Python protocols to define contracts that both database and model adapters must implement:

```python
# Database operations are abstracted through protocols
class DatabaseAdapter(Protocol):
    async def execute_query(self, entity: str, query_spec: QuerySpec) -> list[dict[str, Any]]: ...
    async def execute_create(self, entity: str, data: dict[str, Any]) -> Any: ...
    # ... other methods

# Model operations are abstracted through protocols  
class ModelAdapter(Protocol[T]):
    def serialize(self, instance: T) -> dict[str, Any]: ...
    def deserialize(self, data: dict[str, Any]) -> T: ...
    # ... other methods
```

### Query Specification

All queries are internally represented as `QuerySpec` objects that describe what you want to query:

```python
from acb.models._query import QuerySpec, QueryFilter, QuerySort, SortDirection

# Build a query specification
spec = QuerySpec(
    filter=QueryFilter()
        .where("active", True)
        .where_gt("age", 18)
        .where_in("role", ["admin", "user"]),
    sorts=[QuerySort("created_at", SortDirection.DESC)],
    limit=10,
    offset=20
)
```

## Query Patterns

### Simple Query Style

Perfect for basic CRUD operations with minimal boilerplate:

```python
from acb.models._hybrid import ACBQuery
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    email: str
    active: bool = True

# Setup query interface
query = ACBQuery()
user_query = query.for_model(User)

# Basic operations
users = await user_query.simple.all()
user = await user_query.simple.find(1)
new_user = await user_query.simple.create({"name": "John", "email": "john@example.com"})
await user_query.simple.update(1, {"active": False})
await user_query.simple.delete(1)
```

### Repository Pattern

Ideal for domain-driven design with built-in caching and business logic:

```python
from acb.models._repository import RepositoryOptions, Repository

# Configure repository behavior
repo_options = RepositoryOptions(
    cache_enabled=True,
    cache_ttl=300,
    enable_soft_delete=True,
    audit_enabled=True
)

# Create repository
user_repo = query.for_model(User).repository(repo_options)

# Domain-specific methods
active_users = await user_repo.find_active()
recent_users = await user_repo.find_recent(days=7)

# Batch operations
await user_repo.batch_create([
    {"name": "User 1", "email": "user1@example.com"},
    {"name": "User 2", "email": "user2@example.com"}
])

# Automatic caching
cached_user = await user_repo.find_by_id(1)  # Cached after first access
```

### Specification Pattern

Build complex, reusable business rules:

```python
from acb.models._specification import field, range_spec, custom_spec

# Create individual specifications
active_spec = field("active").equals(True)
adult_spec = field("age").greater_than_or_equal(18)
email_spec = field("email").like("%@company.com")

# Combine specifications
company_employees = active_spec & adult_spec & email_spec

# Use in queries
employees = await query.for_model(User).specification.with_spec(company_employees).all()

# Custom specifications
def vip_user_predicate(user):
    return user.subscription_tier == "premium" and user.total_spent > 1000

vip_spec = custom_spec(
    predicate=vip_user_predicate,
    query_spec=QuerySpec(filter=QueryFilter()
        .where("subscription_tier", "premium")
        .where_gt("total_spent", 1000)
    ),
    name="VIPUser"
)

# Complex business rules
premium_active_employees = company_employees & vip_spec
vip_employees = await query.for_model(User).specification.with_spec(premium_active_employees).all()
```

### Advanced Query Builder

Full control over query construction:

```python
# Complex query building
advanced_query = query.for_model(User).advanced

users = await (advanced_query
    .where("active", True)
    .where_gt("age", 21)
    .where_in("department", ["engineering", "product"])
    .where_not_null("manager_id")
    .order_by_desc("hire_date")
    .limit(50)
    .offset(100)
    .all())

# Aggregations
user_count = await advanced_query.where("active", True).count()
has_managers = await advanced_query.where_not_null("manager_id").exists()

# Bulk operations
await advanced_query.where("last_login", "<", thirty_days_ago).update({"status": "inactive"})
```

### Hybrid Query Interface

Mix and match different query styles:

```python
async def complex_user_operation():
    user_manager = query.for_model(User)
    
    async with user_manager.transaction():
        # Use repository for caching
        active_users = await user_manager.repository().find_active()
        
        # Use specifications for business logic
        premium_spec = field("subscription_tier").equals("premium")
        premium_users = await user_manager.specification.with_spec(premium_spec).all()
        
        # Use advanced queries for bulk operations
        await user_manager.advanced.where_in("id", [u.id for u in premium_users]).update({
            "discount_eligible": True
        })
        
        # Use simple queries for basic operations
        new_admin = await user_manager.simple.create({
            "name": "Admin User",
            "email": "admin@company.com",
            "role": "admin"
        })
```

## Model Adapters

### SQLModel Adapter

Integrates with SQLModel for SQL databases:

```python
from acb.models._sqlmodel import SQLModelAdapter
from sqlmodel import SQLModel, Field

class Product(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    price: float
    category_id: int = Field(foreign_key="category.id")

# Register the adapter
from acb.models._query import registry
registry.register_model_adapter("sqlmodel", SQLModelAdapter())

# Use with query interface
query = ACBQuery(model_adapter_name="sqlmodel")
products = await query.for_model(Product).simple.all()
```

### Pydantic Adapter

Works with Pydantic models for NoSQL databases:

```python
from acb.models._pydantic import PydanticModelAdapter
from pydantic import BaseModel, Field

class User(BaseModel):
    id: str = Field(default=None, alias="_id")
    name: str
    email: str
    tags: list[str] = []

# Register the adapter
registry.register_model_adapter("pydantic", PydanticModelAdapter())

# Use with query interface
query = ACBQuery(model_adapter_name="pydantic")
users = await query.for_model(User).simple.all()
```

## Database Adapters

### SQL Database Adapter

Connects to SQL databases through existing SQL adapters:

```python
from acb.adapters.sql._query import SQLDatabaseAdapter
from acb.adapters import import_adapter

# Get SQL adapter instance
SQL = import_adapter("sql")
sql = depends.get(SQL)

# Create database adapter
sql_adapter = SQLDatabaseAdapter(sql)

# Register with query interface
registry.register_database_adapter("sql", sql_adapter)
```

### NoSQL Database Adapter

Connects to NoSQL databases through existing NoSQL adapters:

```python
from acb.adapters.nosql._query import NoSQLDatabaseAdapter
from acb.adapters import import_adapter

# Get NoSQL adapter instance
NoSQL = import_adapter("nosql")
nosql = depends.get(NoSQL)

# Create database adapter
nosql_adapter = NoSQLDatabaseAdapter(nosql)

# Register with query interface
registry.register_database_adapter("nosql", nosql_adapter)
```

## Configuration

### Basic Setup

```python
from acb.models._hybrid import ACBQuery
from acb.models._query import registry

# Register your adapters
registry.register_database_adapter("sql", sql_adapter, is_default=True)
registry.register_database_adapter("nosql", nosql_adapter)
registry.register_model_adapter("sqlmodel", SQLModelAdapter(), is_default=True)
registry.register_model_adapter("pydantic", PydanticModelAdapter())

# Create query interface
query = ACBQuery()  # Uses default adapters

# Or specify adapters explicitly
query = ACBQuery(
    database_adapter_name="nosql",
    model_adapter_name="pydantic"
)
```

### Repository Configuration

```python
from acb.models._repository import RepositoryOptions

# Default repository options
default_options = RepositoryOptions(
    cache_enabled=True,
    cache_ttl=600,
    batch_size=100,
    enable_soft_delete=False,
    audit_enabled=False
)

# Specific repository options
audit_options = RepositoryOptions(
    cache_enabled=True,
    cache_ttl=300,
    enable_soft_delete=True,
    audit_enabled=True,
    audit_fields=["created_at", "updated_at", "created_by", "updated_by"]
)

# Use with query interface
audited_repo = query.for_model(User).repository(audit_options)
```

## Best Practices

### 1. Use Specifications for Business Logic

```python
# Good: Reusable business rules
active_premium_users = (
    field("active").equals(True) &
    field("subscription_tier").equals("premium") &
    field("payment_status").equals("current")
)

# Use across different query styles
repo_users = await user_repo.find_by_specification(active_premium_users)
spec_users = await query.for_model(User).specification.with_spec(active_premium_users).all()
```

### 2. Choose the Right Query Style

```python
# Simple: Basic CRUD operations
await query.for_model(User).simple.create(user_data)

# Repository: Domain-specific operations with caching
await user_repo.find_active()

# Specification: Complex business rules
await query.for_model(User).specification.with_spec(complex_business_rule).all()

# Advanced: Full control over query building
await query.for_model(User).advanced.where("age", ">", 18).where_in("role", roles).all()
```

### 3. Leverage Caching

```python
# Repository pattern provides automatic caching
cache_enabled_repo = query.for_model(User).repository(
    RepositoryOptions(cache_enabled=True, cache_ttl=300)
)

# Frequently accessed data is cached
user = await cache_enabled_repo.find_by_id(1)  # Cached after first access
```

### 4. Use Transactions for Consistency

```python
async with query.for_model(User).transaction():
    # All operations are atomic
    await query.for_model(User).simple.update(user_id, {"balance": new_balance})
    await query.for_model(Transaction).simple.create(transaction_data)
```

## Examples

### E-commerce Application

```python
from acb.models._hybrid import ACBQuery
from acb.models._specification import field, range_spec
from pydantic import BaseModel

class Product(BaseModel):
    id: str
    name: str
    price: float
    category: str
    stock: int
    active: bool = True

class Order(BaseModel):
    id: str
    user_id: str
    products: list[str]
    total: float
    status: str

# Setup query interface
query = ACBQuery()

# Business logic with specifications
available_products = (
    field("active").equals(True) &
    field("stock").greater_than(0) &
    range_spec("price", 10.0, 1000.0)
)

electronics_spec = field("category").equals("electronics")
affordable_electronics = available_products & electronics_spec

# Repository for caching
product_repo = query.for_model(Product).repository(
    RepositoryOptions(cache_enabled=True, cache_ttl=600)
)

# Complex operations
async def process_order(order_data: dict):
    async with query.for_model(Order).transaction():
        # Find available products
        available = await product_repo.find_by_specification(available_products)
        
        # Create order
        order = await query.for_model(Order).simple.create(order_data)
        
        # Update stock
        for product_id in order_data["products"]:
            await query.for_model(Product).advanced.where("id", product_id).update({
                "stock": F("stock") - 1
            })
        
        return order
```

### Multi-Database Architecture

```python
# Use different databases for different models
class User(SQLModel, table=True):  # SQL database
    id: int = Field(default=None, primary_key=True)
    email: str
    name: str

class UserActivity(BaseModel):  # NoSQL database
    user_id: str
    action: str
    timestamp: datetime
    metadata: dict

# Setup different query interfaces
sql_query = ACBQuery(database_adapter_name="sql", model_adapter_name="sqlmodel")
nosql_query = ACBQuery(database_adapter_name="nosql", model_adapter_name="pydantic")

async def get_user_with_activity(user_id: int):
    # Get user from SQL
    user = await sql_query.for_model(User).simple.find(user_id)
    
    # Get activity from NoSQL
    activity = await nosql_query.for_model(UserActivity).advanced.where("user_id", str(user_id)).limit(10).all()
    
    return {
        "user": user,
        "recent_activity": activity
    }
```

## API Reference

### Core Classes

- `ACBQuery`: Main entry point for query interface
- `Query[T]`: Generic query builder
- `QueryBuilder`: Factory for creating queries
- `QuerySpec`: Query specification object
- `Registry`: Global adapter registry

### Specification Classes

- `Specification[T]`: Base specification class
- `FieldSpecification`: Field-based specifications
- `RangeSpecification`: Range-based specifications
- `CompositeSpecification`: Combined specifications
- `CustomSpecification`: Custom predicate specifications

### Repository Classes

- `Repository[T]`: Base repository class
- `GenericRepository[T]`: Generic repository implementation
- `RepositoryFactory`: Factory for creating repositories
- `RepositoryOptions`: Repository configuration

### Adapter Interfaces

- `DatabaseAdapter`: Protocol for database adapters
- `ModelAdapter[T]`: Protocol for model adapters

For detailed API documentation, see the individual module files:
- [Query Interface](/_query.py)
- [Specification Pattern](/_specification.py)
- [Repository Pattern](/_repository.py)
- [Hybrid Interface](/_hybrid.py)
- [SQLModel Adapter](/_sqlmodel.py)
- [Pydantic Adapter](/_pydantic.py)