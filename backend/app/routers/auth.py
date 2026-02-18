from fastapi import APIRouter, Depends
import urllib.parse

from app.config import settings
from app.core.dependencies import get_token_manager, get_upstox_api
from app.services.token_manager import TokenManager
from app.services.upstox_api import UpstoxAPI
from app.models.schemas import (
    AuthStatus,
    AuthCallback,
    ManualToken,
    LoginUrlResponse,
    TokenValidation,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/status", response_model=AuthStatus)
async def auth_status(tm: TokenManager = Depends(get_token_manager)):
    """Check token validity + expiry info."""
    token_info = await tm.get_token_info()
    if not token_info or not token_info.get("access_token"):
        return AuthStatus(authenticated=False, status="no_token")

    token, status = await tm.get_token_with_auto_refresh()
    return AuthStatus(
        authenticated=token is not None,
        expires_at=token_info.get("expires_at"),
        created_at=token_info.get("created_at"),
        has_refresh_token=token_info.get("has_refresh_token", False),
        status=status,
    )


@router.get("/login-url")
async def login_url():
    """Generate Upstox OAuth2 authorization URL."""
    if not settings.UPSTOX_API_KEY or not settings.UPSTOX_REDIRECT_URL:
        return {"url": None, "error": "API Key and Redirect URL are not configured in backend/.env"}
    params = {
        "client_id": settings.UPSTOX_API_KEY,
        "redirect_uri": settings.UPSTOX_REDIRECT_URL,
        "response_type": "code",
    }
    url = f"https://api.upstox.com/v2/login/authorization/dialog?{urllib.parse.urlencode(params)}"
    return {"url": url, "error": None}


@router.post("/callback")
async def auth_callback(
    body: AuthCallback, tm: TokenManager = Depends(get_token_manager)
):
    """Exchange auth code for access token."""
    token = await tm.get_new_token(body.code)
    if token:
        return {"success": True, "message": "Token saved successfully"}
    return {"success": False, "message": "Failed to exchange auth code for token"}


@router.post("/manual-token")
async def manual_token(
    body: ManualToken, tm: TokenManager = Depends(get_token_manager)
):
    """Save manually entered token."""
    result = await tm.save_token(body.access_token, body.refresh_token, body.expires_in)
    if result:
        return {"success": True, "message": "Token saved successfully"}
    return {"success": False, "message": "Failed to save token"}


@router.post("/refresh")
async def refresh_token(tm: TokenManager = Depends(get_token_manager)):
    """Force token refresh."""
    token, status = await tm.get_token_with_auto_refresh()
    return {"success": token is not None, "status": status}


@router.post("/validate", response_model=TokenValidation)
async def validate_token(api: UpstoxAPI = Depends(get_upstox_api)):
    """Validate token via Upstox profile API."""
    valid, profile, error = await api.validate_token()
    return TokenValidation(valid=valid, profile=profile, error=error)


@router.delete("/token")
async def delete_token(tm: TokenManager = Depends(get_token_manager)):
    """Clear stored token."""
    success = await tm.delete_token()
    return {"success": success}
