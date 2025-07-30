"""
Simple OAuth system integrated with `"mcp[cli]"`
"""

from dotenv import load_dotenv

load_dotenv()

from .client.oauth_client import OAuthClient
from .server.oauth_server import OAuthServer, SimpleAuthSettings, AuthServerSettings
from .server.token_verifier.token_verifier import IntrospectionTokenVerifier
from .server.quick_server import QuickOAuthServerHost

__all__ = [
    "OAuthClient",
    "OAuthServer",
    "QuickOAuthServerHost",
    "IntrospectionTokenVerifier",
    "SimpleAuthSettings",
    "AuthServerSettings",
]
