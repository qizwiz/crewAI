"""
JSON backward compatibility mixin for avoiding Pydantic BaseModel.json() conflicts.

Provides a consistent approach to maintaining backward compatibility when renaming
json properties to avoid conflicts with Pydantic's built-in json() method.
"""

from typing import Optional


class JsonPropertyMixin:
    """
    Mixin that provides backward compatibility for json property access.
    
    Classes that inherit from this mixin should implement a json_output property,
    and this mixin will automatically provide a json property that delegates to it.
    """
    
    @property
    def json(self) -> Optional[str]:
        """
        Backward compatibility property for existing code expecting .json access.
        
        Delegates to json_output to maintain compatibility while avoiding
        conflicts with Pydantic BaseModel.json() method.
        """
        if hasattr(self, 'json_output'):
            return self.json_output
        raise AttributeError(
            f"{self.__class__.__name__} does not implement json_output property"
        )