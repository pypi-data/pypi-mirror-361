import uuid
import jwt
import requests_cache
from requests.exceptions import RequestException
from typing import Dict, Optional
import time
from fastapi import HTTPException

from mcp_kyvos_server.utils.logging import setup_logger
from mcp_kyvos_server.kyvos.auth_config import config
from mcp_kyvos_server.kyvos.mcp_server_url import mcp_server_url
from mcp_kyvos_server.database.token_store import get_tokens, update_token_field

from mcp_kyvos_server.oauth.services.oauth_server_authorization_service import OAuthServerAuthorizationService
from mcp_kyvos_server.oauth.services.oauth_client_authorization_service import OAuthClientAuthorizationService


logger, log_path = setup_logger()
server_auth_service = OAuthServerAuthorizationService()
client_auth_service = OAuthClientAuthorizationService()



# OpenID configuration service.
class OAuthMetadataService:
    def __init__(self, api_url: str = config.KYVOS_API_URL, cache_name: str = "kyvos_cache", cache_expiry_sec: int = 86400):
        self.api_url = api_url
        self.session = requests_cache.CachedSession(
            cache_name=cache_name,
            expire_after=cache_expiry_sec,
            backend="sqlite",
            allowable_methods=("GET",),
        )

    def fetch_openid_configuration(self):
        try:
            response = self.session.get(config.KYVOS_API_URL, timeout=30)
            response.raise_for_status()

            if response.from_cache:
                logger.info("Kyvos API response served from cache.")
            else:
                logger.info("Fetched fresh data from Kyvos API response and cached it.")

            kyvos_details = response.json()
            response_data = kyvos_details.get("RESPONSE", {})

            # Update config dynamically
            config.KYVOS_CLIENT_ID = response_data.get("client_id")
            config.KYVOS_SCOPE = "offline_access openid email profile"  
            config.KYVOS_AUTHORIZE_URL = response_data.get("authorization_url")
            config.KYVOS_TOKEN_URL = response_data.get("token_url")

            metadata = {
                "issuer": f"{mcp_server_url}/",
                "authorization_endpoint": f"{mcp_server_url}/authorize",
                "token_endpoint": f"{mcp_server_url}/token",
                "registration_endpoint": f"{mcp_server_url}/register",
                "scopes_supported": [config.KYVOS_SCOPE],
                "response_types_supported": ["code"],
                "code_challenge_methods_supported": ["S256"],
            }

            logger.info("Well-known API executed successfully and fetched OpenID configuration.")
            return metadata

        except RequestException as e:
            logger.error(f"Error fetching OpenID configuration: {e}")
            return None
        


# Client registration service.
class ClientRegistrationService:
    def __init__(self):
        self._clients: Dict[str, dict] = {}

    def register_client(self, client_req):
        if not client_req["redirect_uris"]:
            raise ValueError("redirect_uris is required")

        registration_access_token = str(uuid.uuid4())

        client_info = client_req.copy()
        client_info.update({
            "client_id": registration_access_token,
        })

        self._clients[registration_access_token] = client_info

        logger.info(f"Client {client_req["client_name"]} registered successfully.")

        return client_info

    def get_client(self, client_id: str) -> Optional[dict]:
        return self._clients.get(client_id)
    



# Server's token generation service.
class AuthService:
    async def handle_callback(self, code: str, code_verifier: str) -> Dict:
        """Exchanges authorization code for tokens and generates bound token."""
        token_response = await server_auth_service.get_oauth_access_token(code, code_verifier)

        access_token = token_response.get("id_token")
        refresh_token = token_response.get("refresh_token")
        id_token = token_response.get("id_token")
        expires_in = token_response.get("expires_in")

        if not access_token:
            logger.error("Access token missing in token response.")
            raise ValueError("Token exchange failed, access token missing.")

        logger.info("Received access token from authorization server.")

        # Decode without verifying signature (just to read payload)
        decoded = jwt.decode(id_token, options={"verify_signature": False})

        # Extract email
        email = decoded.get("email") or decoded.get("sub")

        bound_code = await client_auth_service.generate_bound_code(access_token)
        logger.info(f"Bound authorization code successfully generated for client's access token exchange.")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "id_token": id_token,
            "expires_in": expires_in,
            "bound_code": bound_code,
            "issued_at": time.time(),
            "user_email": email
        }
    



# Client's token generation service.
class TokenService:
    async def get_client_refreshed_access_token(self, email: str) -> dict:       
        client_refresh_token = get_tokens(email)["client_refresh_token"]
        logger.info(f"Received client's refresh token.")

        token_data = await server_auth_service.get_refreshed_oauth_access_token(email, client_refresh_token, "client")
        refreshed_access_token = token_data.get("id_token")

        if not refreshed_access_token:
            logger.error(f"The refresh token is invalid or expired for user - {email}.")
            raise HTTPException(status_code=400, detail="Refresh token is no longer valid. Re-authentication required.")

        # Update database
        update_token_field(email=email, field="client_access_token", value=refreshed_access_token)
        update_token_field(email=email, field="expires_in", value=token_data.get("expires_in"))
        update_token_field(email=email, field="client_refresh_token", value=token_data.get("refresh_token"))

        logger.info(f"New client access token successfully generated and updated in database successfully.")

        return {
            "access_token": refreshed_access_token,
            "token_type": "bearer",
            "expires_in": token_data.get("expires_in"),
            "refresh_token": token_data.get("refresh_token")
        }

    async def get_client_access_token(self, bound_code: str, email: str) -> dict:
        is_bound_code_expired = await client_auth_service.validate_bound_code(bound_code)

        if is_bound_code_expired:
            logger.error("Invalid or expired bound authorization code.")
            raise HTTPException(status_code=400, detail="Invalid or expired code")
        
        logger.info(f"Client access token successfully fetched from database.")
        logger.info(f"Refresh token successfully fetched from database.")

        return {
            "access_token": get_tokens(email)["client_access_token"],
            "token_type": "bearer",
            "expires_in": get_tokens(email)["expires_in"],
            "refresh_token": get_tokens(email)["client_refresh_token"],
        }