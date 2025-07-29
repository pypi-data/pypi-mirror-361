from __future__ import annotations

from http import HTTPStatus

from engrate_sdk import log
from engrate_sdk.http_client.http_client import AsyncClient
from engrate_sdk.types.exceptions import UncontrolledError, ValidationError
from engrate_sdk.types.plugins import BasePluginSpec

log = log.get_logger(__name__)


class PluginRegistry:
    """A registry for managing plugins in the Engrate SDK."""

    def __init__(self, registrar_url: str):
        """Initialize the plugin registry."""
        self.registrar_url = registrar_url

    async def register_plugin(self, plugin: BasePluginSpec):
        """Register a plugin in the registry."""
        if not isinstance(plugin, BasePluginSpec):
            raise TypeError("Plugin must be an instance of BasePluginSpec.")
        if plugin.uid in self.plugins:
            raise ValidationError(f"Plugin with UID {plugin.uid} is already registered.")

        async with AsyncClient() as client:
            response = await client.post(
                self.registrar_url,
                json=plugin.model_dump(),
            )
            if response.status_code != HTTPStatus.OK:
                json = response.json()
                msg = json.get("message", "Unknown error")
                log.error(f"Failed to register plugin: {msg}")
                raise UncontrolledError(f"Failed to register plugin: {response.text}")
