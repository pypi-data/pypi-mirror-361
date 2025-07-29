import os
import uuid
import urllib.parse
from pydantic import ValidationError

from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, HTTPException, Header, status
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from fastapi import APIRouter, HTTPException, status
from fastapi.requests import Request

from mcp_kyvos_server.utils.logging import setup_logger
from mcp_kyvos_server.kyvos.auth_config import config
from mcp_kyvos_server.database.token_store import save_tokens, get_tokens, get_email_by_bound_code, get_tokens_state, get_email_by_client_refresh_token

from mcp_kyvos_server.oauth.services.kyvos_services import OAuthMetadataService
from mcp_kyvos_server.oauth.services.kyvos_services import ClientRegistrationService
from mcp_kyvos_server.oauth.services.models import PKCEManager
from mcp_kyvos_server.oauth.services.kyvos_services import AuthService
from mcp_kyvos_server.oauth.services.kyvos_services import TokenService




logger, log_path = setup_logger()

auth_router = APIRouter()
metadata_service = OAuthMetadataService()
client_service = ClientRegistrationService()
auth_service = AuthService()
token_service = TokenService()




# ----------------------------------------------------------------------------
# Well-Known API to return authorization server metadata.
# ----------------------------------------------------------------------------
@auth_router.get("/.well-known/oauth-authorization-server")
async def authorization_server_metadata(request: Request, mcp_version_protocol: str = Header(None)):
    metadata = metadata_service.fetch_openid_configuration()
    if not metadata:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Failed to fetch OpenID configuration from upstream.")
    return metadata




# ----------------------------------------------------------------------------
# Register API to register the client and get its callback URL.
# ----------------------------------------------------------------------------
@auth_router.post("/register")
async def register_client(request: Request):
    try:
        body = await request.json()
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.errors())
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON payload.")

    try:
        client_resp = client_service.register_client(body)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return client_resp




# ----------------------------------------------------------------------------
# Authorize API to construct authorization url and redirect user to browser.
# ----------------------------------------------------------------------------
@auth_router.get("/authorize")
async def authorize(request: Request):
    params = request.query_params
    state = params.get("state") or str(uuid.uuid4())
    client_id = params.get("client_id")
    redirect_uri = params.get("redirect_uri")

    client = client_service.get_client(client_id)
    if client is None:
        logger.warning("Client didn't registered via register endpoint. Received client callback url through authorize params.")
        client_redirect_uri = redirect_uri 
    else:
        client_redirect_uri = redirect_uri or client["redirect_uris"][0]

    # Generate PKCE code challenge pair if not present
    code_verifier, code_challenge = await PKCEManager.create_code_challenge_pair()

    # Update database with token details
    db_token_data = {
        "code_verifier": code_verifier,
        "code_challenge": code_challenge,
        "client_redirect_uri": client_redirect_uri
    }
    save_tokens(state, db_token_data)

    login_hint = "username"

    # Construct authorization URL
    auth_url = (
        f"{config.KYVOS_AUTHORIZE_URL}?"
        f"response_type=code&client_id={config.KYVOS_CLIENT_ID}"
        f"&redirect_uri={config.REDIRECT_URI}"
        f"&scope={config.KYVOS_SCOPE}"
        f"&state={state}"
        f"&code_challenge={code_challenge}"
        f"&code_challenge_method=S256"
        f"&prompt=login&login_hint={login_hint}"
    )

    logger.info(f"Redirecting client to authorization URL.")
    return RedirectResponse(auth_url)




# ----------------------------------------------------------------------------
# Callback URL to receive authorization code and exchange it for access token.
# ----------------------------------------------------------------------------
@auth_router.get("/auth/callback")
async def callback(request: Request):
    params = request.query_params
    state = params.get("state")
    code = params.get("code")

    if not code:
        logger.error("Authorization code missing in callback.")
        raise HTTPException(status_code=400, detail="Missing authorization code.")

    if not state:
        logger.error("State parameter missing; cannot identify database.")
        raise HTTPException(status_code=400, detail="Missing state identifier.")

    code_verifier = get_tokens_state(state)["code_verifier"]

    if not code_verifier:
        logger.error("Code verifier missing from database.")
        raise HTTPException(status_code=400, detail="Missing code verifier in database.")

    try:
        token_data = await auth_service.handle_callback(code, code_verifier)
    except Exception as e:
        logger.error(f"Error during token exchange or bound token generation: {e}")
        error_message = urllib.parse.quote("Token exchange failed. Please try again.")
        return RedirectResponse(f"/?error={error_message}")

    client_redirect_uri = get_tokens_state(state)["client_redirect_uri"]
    redirect_uri = f"{client_redirect_uri}?code={token_data['bound_code']}&state={state}"
    logger.info(f"Redirecting to client callback URL with bound code.")

    authorized_user_email = token_data["user_email"]

    # Update database with token details
    db_token_data = {
        "email": token_data["user_email"],
        "auth_code": code,
        "bound_issued": token_data["issued_at"],
        "bound_code": token_data["bound_code"],
        "token_issued_at": token_data["issued_at"],
        "access_token": token_data["id_token"],
        "refresh_token": token_data["refresh_token"],
        "id_token": token_data["id_token"],
        "expires_in": token_data["expires_in"],
        "client_refresh_token": token_data["refresh_token"],
        "client_access_token": token_data["id_token"],
    }

    save_tokens(state, db_token_data)
    logger.info(f"Updated token details in database.")

    return RedirectResponse(redirect_uri)




# ----------------------------------------------------------------------------
# Token API to receive bound code from client and return it access token.
# ----------------------------------------------------------------------------
@auth_router.post("/token")
async def generate_client_access_token(request: Request):
    logger.info(f"Generating access token for MCP Client.")
    body = await request.body()
    parsed = urllib.parse.parse_qs(body.decode())

    bound_auth_code = parsed.get("code", [None])[0]
    refresh_token = parsed.get("refresh_token", [None])[0]

    if refresh_token:
        email_id = get_email_by_client_refresh_token(refresh_token)
        logger.info(f"Client access token expired.")
        logger.info("Processing refresh token to obtain new client access token.")
        return await token_service.get_client_refreshed_access_token(email_id)

    if not bound_auth_code:
        logger.error("Missing 'code' parameter in request.")
        raise HTTPException(status_code=400, detail="Missing authorization code")

    user_email_id = get_email_by_bound_code(bound_auth_code)
    logger.info("Processing the bound authorization code to generate client access token.")
    
    tokens = await token_service.get_client_access_token(bound_auth_code, user_email_id) 
    logger.info("OAuth flow completed successfully: Client access token issued and sent to the client.") 
    return tokens




# ----------------------------------------------------------------------------
# Error page redirection, if the token exchange fails.
# ----------------------------------------------------------------------------
base_dir = os.path.dirname(os.path.dirname(__file__))
templates_dir = os.path.join(base_dir, "templates")
templates = Jinja2Templates(directory=templates_dir)

@auth_router.get("/")
async def home(request: Request):
    error_message = request.query_params.get("error")
    return templates.TemplateResponse("index.html", {"request": request, "error": error_message})