"""
Centralized model factory for handling Pydantic create_model type issues.

This module provides type-safe wrappers around pydantic.create_model to avoid
mypy call-overload errors throughout the codebase.
"""

from typing import Any, Dict, Optional, Type

from pydantic import BaseModel, create_model


def create_tool_schema(
    model_name: str, 
    field_definitions: Dict[str, Any],
    base_class: Optional[Type[BaseModel]] = None
) -> Type[BaseModel]:
    """
    Create a Pydantic model for tool schemas with proper type handling.
    
    Args:
        model_name: Name for the generated model class
        field_definitions: Dict mapping field names to field definitions
        base_class: Optional base class for the model
        
    Returns:
        Generated Pydantic model class
    """
    if base_class:
        return create_model(model_name, __base__=base_class, **field_definitions)  # type: ignore[call-overload]
    else:
        return create_model(model_name, **field_definitions)  # type: ignore[call-overload]


def create_args_schema(
    model_name: str,
    field_definitions: Dict[str, Any]
) -> Type[BaseModel]:
    """
    Create a Pydantic model specifically for tool arguments.
    
    Args:
        model_name: Name for the generated model class  
        field_definitions: Dict mapping field names to (type, Field) tuples
        
    Returns:
        Generated Pydantic model class
    """
    return create_model(model_name, **field_definitions)  # type: ignore[call-overload]