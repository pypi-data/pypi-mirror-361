"""
Structured output support module.
"""

from typing import Dict, Any, Type, Optional
from pydantic import BaseModel
import json


class StructuredOutput:
    """
    Structured output helper class for generating JSON Schema and handling structured responses.
    """
    
    @staticmethod
    def from_pydantic(model_class: Type[BaseModel]) -> Dict[str, Any]:
        """
        Generate JSON Schema from Pydantic model.
        
        Args:
            model_class: Pydantic model class
            
        Returns:
            JSON Schema dictionary
        """
        return model_class.model_json_schema()
    
    @staticmethod
    def from_dict(schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate JSON Schema from dictionary.
        
        Args:
            schema: Schema dictionary
            
        Returns:
            JSON Schema dictionary
        """
        return schema
    
    @staticmethod
    def json_mode() -> str:
        """
        Return JSON mode identifier.
        
        Returns:
            "json" string
        """
        return "json"
    
    @staticmethod
    def parse_response(response: str, model_class: Optional[Type[BaseModel]] = None) -> Any:
        """
        Parse structured response.
        
        Args:
            response: Response string
            model_class: Optional Pydantic model class
            
        Returns:
            Parsed object
        """
        try:
            data = json.loads(response)
            if model_class:
                return model_class.model_validate(data)
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Unable to parse JSON response: {e}")
        except Exception as e:
            raise ValueError(f"Unable to validate response data: {e}")


# Convenience functions
def create_json_schema(model_class: Type[BaseModel]) -> Dict[str, Any]:
    """
    Convenience function to create JSON Schema.
    
    Args:
        model_class: Pydantic model class
        
    Returns:
        JSON Schema dictionary
    """
    return StructuredOutput.from_pydantic(model_class)


def json_format() -> str:
    """
    Convenience function to return JSON format identifier.
    
    Returns:
        "json" string
    """
    return StructuredOutput.json_mode()


# Common JSON Schema examples
COMMON_SCHEMAS = {
    "person": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "email": {"type": "string", "format": "email"}
        },
        "required": ["name", "age"]
    },
    "product": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "price": {"type": "number"},
            "category": {"type": "string"},
            "in_stock": {"type": "boolean"}
        },
        "required": ["name", "price"]
    },
    "summary": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "content": {"type": "string"},
            "keywords": {"type": "array", "items": {"type": "string"}},
            "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]}
        },
        "required": ["title", "content"]
    }
} 