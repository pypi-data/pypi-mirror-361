from typing import Dict, Any, Type, Optional
from pydantic import BaseModel, Field, create_model


class DynamicUtility:

    @staticmethod
    def create_pydantic_base_model(title: str, entities: Dict[str, Dict[str, Any]]) -> Type[BaseModel]:
        supported_types = {int, str, float, list}
        model_fields = {}

        for field_name, config in entities.items():
            field_type = config.get("type")
            description = config.get("description", "")

            if field_type not in supported_types:
                raise ValueError(f"Unsupported type for field '{field_name}': {field_type}")

            optional_type = Optional[field_type]
            model_fields[field_name] = (optional_type, Field(default=None, description=description))

        return create_model(title, **model_fields)