import os 
from mcp_kyvos_server.utils.constants import EnvironmentVariables

class BaseURLMiddleware:
    def __init__(self):
        self.protocol = "https" if os.getenv('SSL_KEY_FILE') else "http"
        self.hostname = self._get_hostname()
        self.port = os.getenv(EnvironmentVariables.PORT, "8000")
        self.mcp_server_url = f"{self.protocol}://{self.hostname}:{self.port}"

    def _get_hostname(self):
        mcp_server_url_env = os.getenv(EnvironmentVariables.MCP_SERVER_HOSTNAME)
        if mcp_server_url_env:
            return mcp_server_url_env
        return "127.0.0.1"

    def get_mcp_server_url(self):
        return self.mcp_server_url

mcp_server_url_middleware = BaseURLMiddleware()
mcp_server_url = mcp_server_url_middleware.get_mcp_server_url()