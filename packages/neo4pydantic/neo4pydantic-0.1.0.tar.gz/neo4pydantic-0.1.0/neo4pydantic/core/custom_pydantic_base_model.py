from pydantic import BaseModel, model_validator
from typing import Dict, Any
from neo4pydantic.utils.types import neo4j_type_convertor


class CustomBaseModel(BaseModel):
    """Base model with automatic type conversion support"""

    @model_validator(mode="before")
    @classmethod
    def auto_convert_types(cls, data: Any) -> Any:
        """Automatically convert registered types"""
        if isinstance(data, dict):
            return cls._convert_dict(data)
        elif isinstance(data, (list, tuple)):
            return cls._convert_sequence(data)
        else:
            return cls._convert_value(data)

    @classmethod
    def _convert_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert values in a dictionary"""
        converted = {}
        for key, value in data.items():
            converted[key] = cls._convert_value(value)
        return converted

    @classmethod
    def _convert_sequence(cls, data) -> list:
        """Convert values in a sequence"""
        return [cls._convert_value(item) for item in data]

    @classmethod
    def _convert_value(cls, value: Any) -> Any:
        """Convert a single value if converter exists"""
        value_type = type(value)
        if value_type in neo4j_type_convertor:
            return neo4j_type_convertor[value_type](value)
        elif isinstance(value, dict):
            return cls._convert_dict(value)
        elif isinstance(value, (list, tuple)):
            return cls._convert_sequence(value)
        return value
