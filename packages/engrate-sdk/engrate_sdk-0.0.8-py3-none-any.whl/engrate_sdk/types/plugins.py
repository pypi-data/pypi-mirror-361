"""Types and base classes for plugins in the Engrate SDK.

This module defines the BasePlugin class and related types for plugin development.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel

from engrate_sdk import log
from engrate_sdk.types.exceptions import ParseError, UnsetError

log = log.get_logger(__name__)

class BasePluginSpec(BaseModel):
    """Base class for all plugins in the Engrate SDK.

    This class provides a common interface for plugins, ensuring they can be initialized
    and have a name.
    """
    uid:UUID | None = None
    name: str
    author:str
    description: str | None  = None
    enabled:bool = False
    plugin_metadata:dict[str,Any] = []

    def __init__(self, **data):
        """Initialize the plugin with the provided data."""
        super().__init__(**data)
        if not self.uid:
            self.uid = UUID(int=0)
        self.__validate()

    def __validate(self):
        """Validate the plugin's configuration.

        This method can be overridden by subclasses.
        """
        if not self.name:
            raise UnsetError("Plugin name must be set.")
        if not self.author:
            raise UnsetError("Plugin author must be set.")
        if not isinstance(self.enabled, bool):
            raise ParseError("Plugin enabled must be a boolean value.")
        if not isinstance(self.plugin_metadata, dict):
            raise ParseError("Plugin metadata must be a dictionary.")


