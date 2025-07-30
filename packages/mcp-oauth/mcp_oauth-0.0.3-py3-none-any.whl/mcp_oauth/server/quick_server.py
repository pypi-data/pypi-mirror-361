"""This module provides a simple OAuth server host implementation and CLI entrypoint.

It defines default configuration values, a class to encapsulate OAuth server settings and startup logic,
and a Click-based command-line interface for launching the server.
"""

import os
import click

if __name__ == "__main__":
    from oauth_server import (
        OAuthServer,
        SimpleAuthSettings,
        AuthServerSettings,
    )
else:

    from .oauth_server import (
        OAuthServer,
        SimpleAuthSettings,
        AuthServerSettings,
    )

DEFAULT_OAUTH_HOST: str = "127.0.0.1"
DEFAULT_OAUTH_PORT: int = 8080


class QuickOAuthServerHost:
    """
    QuickOAuthServerHost encapsulates the configuration and startup logic for a simple OAuth server.

    Attributes:
        oauth_host (str): Host address for the OAuth server.
        oauth_port (int): Port number for the OAuth server.
        oauth_server_url (str): Internal URL for the OAuth server.
        superusername (str | None): Superuser username for authentication.
        superuserpassword (str | None): Superuser password for authentication.
    """

    def __init__(
        self,
        oauth_host: str = DEFAULT_OAUTH_HOST,
        oauth_port: int = DEFAULT_OAUTH_PORT,
        superusername: str | None = os.getenv("SUPERUSERNAME"),
        superuserpassword: str | None = os.getenv("SUPERUSERPASSWORD"),
        mcp_scope: str = "user",
        # mcp_scopes: list[str] = ["user"],
    ):
        """Initializes the SimpleOAuthServerHost with configuration for the OAuth server.

        Args:
            oauth_host (str): Host address for the OAuth server.
            oauth_port (int): Port number for the OAuth server.
            superusername (str | None): Superuser username for authentication.
            superuserpassword (str | None): Superuser password for authentication.
        """
        self.oauth_host: str = oauth_host
        self.oauth_port: int = oauth_port
        self.oauth_server_url: str = f"http://{oauth_host}:{oauth_port}"

        self.superusername: str = superusername
        self.superuserpassword: str = superuserpassword

        self.mcp_scope: str = mcp_scope
        # self.mcp_scopes: list[str] = mcp_scopes

    @property
    def __auth_settings(self) -> SimpleAuthSettings:
        return SimpleAuthSettings(
            superusername=self.superusername,
            superuserpassword=self.superuserpassword,
            mcp_scope=self.mcp_scope,
        )

    @property
    def __server_settings(self) -> AuthServerSettings:
        return AuthServerSettings(
            host=self.oauth_host,
            port=self.oauth_port,
            server_url=f"{self.oauth_server_url}",
            auth_callback_path=f"{self.oauth_server_url}/login",
        )

    def run_oauth_server(self):

        oauth_server: OAuthServer = OAuthServer(
            server_settings=self.__server_settings,
            auth_settings=self.__auth_settings,
        )
        oauth_server.run_starlette_server()


@click.command()
@click.option("--host", default="127.0.0.1", help="")
@click.option("--port", default=9080, help="Port to listen on")
@click.option("--superusername", default=None, help="")
@click.option("--superuserpassword", default=None, help="")
def main(
    host: str,
    port: int,
    superusername: str | None,
    superuserpassword: str | None,
):
    simple_oauth_server_host: QuickOAuthServerHost = QuickOAuthServerHost(
        oauth_port=port,
        oauth_host=host,
        superusername=superusername,
        superuserpassword=superuserpassword,
    )
    simple_oauth_server_host.run_oauth_server()


if __name__ == "__main__":
    main()
