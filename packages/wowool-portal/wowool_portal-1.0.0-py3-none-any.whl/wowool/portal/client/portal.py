from wowool.portal.client.defines import (
    WOWOOL_PORTAL_API_KEY_ENV_NAME,
    WOWOOL_PORTAL_HOST_DEFAULT,
    WOWOOL_PORTAL_HOST_ENV_NAME,
)
from wowool.portal.client.environment import resolve_variable
from wowool.portal.client.service import Service
from wowool.portal.client.version import get_version


class Portal:
    """
    Portal client for connecting to the Portal server.

    This class holds the information required to connect to the Portal server.
    An instance of this class is used by a Pipeline so that the latter is
    able to send the required requests.

    .. literalinclude:: init_pipeline_context.py
        :language: python
    """

    def __init__(self, api_key: str | None = None, host: str | None = None):
        self._api_key = resolve_variable(WOWOOL_PORTAL_API_KEY_ENV_NAME, api_key)
        self._host = resolve_variable(WOWOOL_PORTAL_HOST_ENV_NAME, host or WOWOOL_PORTAL_HOST_DEFAULT)
        headers = {
            "X-API-Key": self._api_key,
            "X-Client-Agent": "wowool-portal-python",
            "X-Client-Version": get_version(),
        }
        self._service = Service(self._host, headers)

    def __repr__(self):
        return f"""Portal(host="{self._host}", api_key="***{self._api_key[-3:]}")"""
