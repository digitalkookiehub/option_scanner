"""
Token Manager - Async port of ScreenerV13.py TokenManager (lines 1445-1608).
All logic preserved exactly, only converted from requests to httpx and sqlite3 to asyncpg.
"""
import asyncpg
import httpx
from datetime import datetime, timedelta

from app.config import settings
from app.repositories import token_repository


class TokenManager:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def save_token(self, access_token, refresh_token=None, expires_in=None):
        try:
            expires_at = (
                (datetime.now() + timedelta(seconds=expires_in)).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                if expires_in
                else None
            )
            success = await token_repository.save_token(
                self.pool, access_token, refresh_token, expires_at
            )
            return access_token if success else None
        except Exception:
            return None

    async def get_token(self):
        try:
            result = await token_repository.get_latest_token(self.pool)
            if result:
                access_token = result["access_token"]
                refresh_token = result["refresh_token"]
                expires_at = result["expires_at"]
                if expires_at:
                    if datetime.strptime(
                        expires_at, "%Y-%m-%d %H:%M:%S"
                    ) <= datetime.now() + timedelta(hours=1):
                        return (
                            await self.refresh_token_method(refresh_token)
                            if refresh_token
                            else None
                        )
                return access_token
            return None
        except Exception:
            return None

    async def get_token_with_auto_refresh(self):
        """Get token and auto-refresh if expired"""
        try:
            result = await token_repository.get_latest_token(self.pool)

            if result:
                access_token = result["access_token"]
                refresh_token = result["refresh_token"]
                expires_at = result["expires_at"]

                # Check if token is expired or about to expire (within 1 hour)
                if expires_at:
                    try:
                        expiry_time = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
                        if expiry_time <= datetime.now() + timedelta(minutes=30):
                            # Token expired or expiring soon - try to refresh
                            if refresh_token:
                                new_token = await self.refresh_token_method(refresh_token)
                                if new_token:
                                    return new_token, "refreshed"
                                else:
                                    return None, "refresh_failed"
                            else:
                                return None, "no_refresh_token"
                    except Exception:
                        pass

                return access_token, "valid"
            return None, "no_token"
        except Exception as e:
            return None, f"error: {str(e)}"

    async def refresh_token_method(self, refresh_token):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.UPSTOX_TOKEN_URL,
                    data={
                        "refresh_token": refresh_token,
                        "client_id": settings.UPSTOX_API_KEY,
                        "client_secret": settings.UPSTOX_API_SECRET,
                        "grant_type": "refresh_token",
                    },
                    timeout=10,
                )
            if response.status_code == 200:
                data = response.json()
                new_access_token = data.get("access_token")
                new_refresh_token = data.get("refresh_token", refresh_token)
                expires_in = data.get("expires_in", 86400)  # Default 24 hours
                await self.save_token(new_access_token, new_refresh_token, expires_in)
                return new_access_token
            elif response.status_code == 401:
                # Refresh token also expired - need full re-auth
                return None
        except Exception:
            pass
        return None

    async def get_token_info(self):
        """Get detailed token information"""
        try:
            result = await token_repository.get_latest_token(self.pool)

            if result:
                return {
                    "access_token": result["access_token"],
                    "refresh_token": result["refresh_token"],
                    "expires_at": result["expires_at"],
                    "created_at": result["created_at"],
                    "has_refresh_token": result["refresh_token"] is not None
                    and len(result["refresh_token"]) > 0,
                }
            return None
        except Exception:
            return None

    async def get_new_token(self, auth_code):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.UPSTOX_TOKEN_URL,
                    data={
                        "client_id": settings.UPSTOX_API_KEY,
                        "client_secret": settings.UPSTOX_API_SECRET,
                        "redirect_uri": settings.UPSTOX_REDIRECT_URL,
                        "code": auth_code,
                        "grant_type": "authorization_code",
                    },
                    timeout=10,
                )
            if response.status_code == 200:
                data = response.json()
                await self.save_token(
                    data.get("access_token"),
                    data.get("refresh_token"),
                    data.get("expires_in"),
                )
                return data.get("access_token")
        except Exception:
            pass
        return None

    async def delete_token(self):
        """Delete stored token."""
        return await token_repository.delete_token(self.pool)
