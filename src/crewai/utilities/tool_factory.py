"""
Intelligent tool factory with parameter adaptation.

This module provides a centralized factory for creating tool instances with
automatic parameter adaptation based on the target class constructor signature.
Eliminates the need for scattered parameter handling across tool creation sites.
"""

import inspect
from typing import Any, Dict, Type, TypeVar

from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


class ToolFactory:
    """
    Intelligent factory for creating tool instances with automatic parameter adaptation.
    
    This factory inspects the target class constructor and adapts parameters accordingly,
    eliminating the common "unexpected keyword argument" errors in tool creation.
    """
    
    @staticmethod
    def create_compatible(
        cls: Type[T], 
        source_tool: Any, 
        args_schema: Type[BaseModel],
        **additional_kwargs: Any
    ) -> T:
        """
        Create a tool instance with intelligent parameter adaptation.
        
        Args:
            cls: Target tool class to instantiate
            source_tool: Source tool object with attributes to copy
            args_schema: Pydantic schema for tool arguments  
            **additional_kwargs: Additional parameters to include
            
        Returns:
            Instance of cls with appropriate parameters
        """
        # Get constructor signature
        sig = inspect.signature(cls.__init__)
        valid_params = set(sig.parameters.keys()) - {'self'}
        
        # Build parameter dict from source tool
        params = {}
        
        # Standard parameters that most tools accept
        standard_mappings = {
            'name': lambda: getattr(source_tool, 'name', 'Unnamed Tool'),
            'description': lambda: getattr(source_tool, 'description', ''),
            'args_schema': lambda: args_schema,
        }
        
        # Optional parameters that only some tools accept
        optional_mappings = {
            'func': lambda: getattr(source_tool, 'func', None),
            'result_as_answer': lambda: getattr(source_tool, 'result_as_answer', False),
            'cache_function': lambda: getattr(source_tool, 'cache_function', None),
        }
        
        # Add standard parameters if the constructor accepts them
        for param_name, value_func in standard_mappings.items():
            if param_name in valid_params:
                params[param_name] = value_func()
        
        # Add optional parameters if the constructor accepts them
        for param_name, value_func in optional_mappings.items():
            if param_name in valid_params:
                value = value_func()
                if value is not None:
                    params[param_name] = value
        
        # Add any additional kwargs if the constructor accepts them
        for param_name, value in additional_kwargs.items():
            if param_name in valid_params:
                params[param_name] = value
        
        # Create instance with adapted parameters
        return cls(**params)
    
    @staticmethod
    def get_constructor_info(cls: Type) -> Dict[str, Any]:
        """
        Get information about a class constructor for debugging.
        
        Args:
            cls: Class to inspect
            
        Returns:
            Dictionary with constructor parameter information
        """
        sig = inspect.signature(cls.__init__)
        return {
            'class_name': cls.__name__,
            'parameters': list(sig.parameters.keys()),
            'required_params': [
                name for name, param in sig.parameters.items() 
                if param.default == param.empty and name != 'self'
            ],
            'optional_params': [
                name for name, param in sig.parameters.items() 
                if param.default != param.empty
            ]
        }