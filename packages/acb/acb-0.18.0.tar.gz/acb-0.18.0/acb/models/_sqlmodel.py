"""SQLModel Adapter for Universal Query Interface.

This module implements the ModelAdapter protocol for SQLModel models,
allowing the universal query interface to work with SQLModel classes.
"""

import inspect
from typing import Any, TypeVar, get_args, get_origin

from acb.models._query import ModelAdapter

try:
    from sqlmodel import SQLModel

    SQLMODEL_AVAILABLE = True
except ImportError:
    SQLMODEL_AVAILABLE = False

    class SQLModel:
        pass


T = TypeVar("T", bound=SQLModel)


class SQLModelAdapter(ModelAdapter[T]):
    def __init__(self) -> None:
        if not SQLMODEL_AVAILABLE:
            msg = "SQLModel is required for SQLModelAdapter"
            raise ImportError(msg)

    def serialize(self, instance: T) -> dict[str, Any]:
        if hasattr(instance, "model_dump"):
            return instance.model_dump()
        if hasattr(instance, "dict"):
            return instance.dict()
        return self._manual_serialize(instance)

    def _manual_serialize(self, instance: T) -> dict[str, Any]:
        result = {}
        if hasattr(instance, "__fields__"):
            for field_name in instance.__fields__:
                if hasattr(instance, field_name):
                    value = getattr(instance, field_name)
                    result[field_name] = self._serialize_value(value)
        else:
            for attr_name in dir(instance):
                if not attr_name.startswith("_") and not callable(
                    getattr(instance, attr_name),
                ):
                    value = getattr(instance, attr_name)
                    result[attr_name] = self._serialize_value(value)

        return result

    def _serialize_value(self, value: Any) -> Any:
        if isinstance(value, SQLModel):
            return self.serialize(value)
        if isinstance(value, list):
            return [self._serialize_value(item) for item in value]
        if isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        return value

    def deserialize(self, data: dict[str, Any]) -> T:
        msg = "Deserialize requires specific model class context"
        raise NotImplementedError(msg)

    def deserialize_to_class(self, model_class: type[T], data: dict[str, Any]) -> T:
        try:
            return model_class(**data)
        except Exception:
            filtered_data = self._filter_data_for_model(model_class, data)
            return model_class(**filtered_data)

    def _filter_data_for_model(
        self,
        model_class: type[T],
        data: dict[str, Any],
    ) -> dict[str, Any]:
        if hasattr(model_class, "__fields__"):
            model_fields = set(model_class.__fields__.keys())
        elif hasattr(model_class, "model_fields"):
            model_fields = set(model_class.model_fields.keys())
        else:
            return data

        return {k: v for k, v in data.items() if k in model_fields}

    def get_entity_name(self, model_class: type[T]) -> str:
        if hasattr(model_class, "__tablename__"):
            return model_class.__tablename__
        if hasattr(model_class, "__table__") and hasattr(
            model_class.__table__,
            "name",
        ):
            return model_class.__table__.name
        return model_class.__name__.lower()

    def get_field_mapping(self, model_class: type[T]) -> dict[str, str]:
        field_mapping = {}
        if hasattr(model_class, "__fields__"):
            for field_name, field_info in model_class.__fields__.items():
                if hasattr(field_info, "alias") and field_info.alias:
                    field_mapping[field_name] = field_info.alias
                else:
                    field_mapping[field_name] = field_name
        elif hasattr(model_class, "model_fields"):
            for field_name, field_info in model_class.model_fields.items():
                if hasattr(field_info, "alias") and field_info.alias:
                    field_mapping[field_name] = field_info.alias
                else:
                    field_mapping[field_name] = field_name
        elif hasattr(model_class, "__annotations__"):
            for field_name in model_class.__annotations__:
                field_mapping[field_name] = field_name

        return field_mapping

    def validate_data(
        self,
        model_class: type[T],
        data: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            temp_instance = model_class(**data)
            return self.serialize(temp_instance)
        except Exception:
            filtered_data = self._filter_data_for_model(model_class, data)
            temp_instance = model_class(**filtered_data)
            return self.serialize(temp_instance)

    def get_primary_key_field(self, model_class: type[T]) -> str:
        if hasattr(model_class, "__table__"):
            for column in model_class.__table__.columns:
                if column.primary_key:
                    return column.name
        common_pk_names = ["id", "pk", "primary_key", "_id"]
        if hasattr(model_class, "__fields__"):
            for field_name in model_class.__fields__:
                if field_name in common_pk_names:
                    return field_name
        elif hasattr(model_class, "model_fields"):
            for field_name in model_class.model_fields:
                if field_name in common_pk_names:
                    return field_name

        return "id"

    def get_field_type(self, model_class: type[T], field_name: str) -> type:
        if hasattr(model_class, "__fields__"):
            field_info = model_class.__fields__.get(field_name)
            if field_info:
                return field_info.type_
        elif hasattr(model_class, "model_fields"):
            field_info = model_class.model_fields.get(field_name)
            if field_info:
                return field_info.annotation
        elif hasattr(model_class, "__annotations__"):
            return model_class.__annotations__.get(field_name, Any)

        return Any

    def is_relationship_field(self, model_class: type[T], field_name: str) -> bool:
        if hasattr(model_class, "__table__"):
            if hasattr(model_class.__table__.columns, field_name):
                column = getattr(model_class.__table__.columns, field_name)
                return bool(column.foreign_keys)
        field_type = self.get_field_type(model_class, field_name)
        if hasattr(field_type, "__origin__"):
            origin = get_origin(field_type)
            if origin in (list,):
                args = get_args(field_type)
                if args and issubclass(args[0], SQLModel):
                    return True
        return bool(inspect.isclass(field_type) and issubclass(field_type, SQLModel))
