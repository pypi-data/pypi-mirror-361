"""Mock plugin registrar for engrate_sdk.

This module provides a FastAPI app with endpoints to register plugins for testing
purposes.
"""

from uuid import UUID

from fastapi import FastAPI
from starlette import status

from engrate_sdk.http import server
from engrate_sdk.http.server import ServerConf
from engrate_sdk.types.plugins import BasePluginSpec
from engrate_sdk.utils import log

logger = log.get_logger(__name__)

app = FastAPI()


@app.post(
    "/plugins",
    status_code=status.HTTP_201_CREATED,
    response_model=BasePluginSpec,
    description="Register a new plugin",
)
async def register_plugin(plugin: BasePluginSpec):
    """Mock endpoint to register a new plugin.

    Parameters
    ----------
    plugin : BasePluginSpec
        The plugin specification to register.

    Returns:
    -------
    BasePluginSpec
        The registered plugin with a new UUID assigned.
    """
    log.info(f"Registering plugin: {plugin.name} by {plugin.author}")
    uuid = UUID()
    plugin.uid = uuid
    return plugin


if __name__ == "__main__":
    config = ServerConf(port=8899, host="0.0.0.0", debug=True, autoreload=True)  # noqa: S104
    server.run(config, "mock_registrar:app")
