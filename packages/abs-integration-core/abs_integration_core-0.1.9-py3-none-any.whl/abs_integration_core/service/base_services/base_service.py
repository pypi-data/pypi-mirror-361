from datetime import UTC, datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Protocol

import httpx
from fastapi import Request

from abs_integration_core.schema import Integration, Subscription, TokenData


class IntegrationServiceProtocol(Protocol):
    """Protocol defining the interface for integration services"""

    def get_auth_url(self, state: Optional[Dict] = None) -> Dict[str, str]:
        """
        Generate an authentication URL for OAuth flow.

        Args:
            state: Optional state dictionary to include in the OAuth flow

        Returns:
            A dictionary containing the auth URL and other necessary information
        """
        ...

    async def handle_oauth_callback(self, code: str, user_id: int) -> TokenData:
        """
        Handle the OAuth callback and store tokens.

        Args:
            code: The authorization code from OAuth callback

        Returns:
            TokenData object
        """
        ...

    async def get_query_by_user_id(self, user_id: int):
        """Get the integration query by user_id"""
        ...

    async def get_all_integrations(
        self, user_id: int, page: int = 1, page_size: int = 10
    ) -> List[Integration]:
        """
        Get all integrations.

        Returns:
            List of TokenData objects
        """
        ...
    
    async def get_all_integrations_by_provider(
        self
    ) -> List[Integration]:
        """
        Get all integrations.

        Returns:
            List of TokenData objects
        """
        ...

    async def refresh_token(
        self, token_url: str, refresh_data: Dict, user_id: int
    ) -> Optional[TokenData]:
        """
        Refresh the access token using the refresh token.

        Returns:
            Updated TokenData if successful, None otherwise
        """
        ...

    async def get_integration(self, user_id: int) -> Optional[TokenData]:
        """
        Get integration data.

        Returns:
            TokenData if integration exists, None otherwise
        """
        ...

    async def delete_integration(self, user_id: int) -> bool:
        """
        Delete an integration.

        Returns:
            True if deleted, False otherwise
        """
        ...

    async def get_resource_subscription_method(self, resource_type: str) -> Callable:
        """
        Get the subscription method for a resource type.
        """
        ...

    async def subscribe(
        self,
        user_id: int,
        target_url: str,
        site_id: str,
        resource_id: str,
        event_types: List[str] = ["created", "updated", "deleted"],
        expiration_days: int = 3,
    ) -> Dict:
        """
        Subscribe to a resource.
        """
        ...

    async def create_subscription(
        self,
        resource: str,
        change_type: str = "created,updated,deleted",
        expiration_days: int = 3,
    ) -> Dict:
        """
        Create a subscription for a resource.
        """
        ...

    async def renew_subscription(
        self, subscription_id: str, expiration_days: int = 3
    ) -> Dict:
        """
        Renew a subscription.
        """
        ...

    async def delete_subscription(self, subscription_id: str, user_id: int) -> None:
        """
        Delete a subscription.
        """
        ...

    async def list_subscriptions(
        self, user_id: int, page: int = 1, page_size: int = 10
    ) -> List[Subscription]:
        """
        List all subscriptions.
        """
        ...

    async def get_resource_path(
        self, resource_type: str, site_id: str, resource_id: str
    ) -> str:
        """
        Get the resource path for a SharePoint resource.
        """
        ...

    async def list_resources(self) -> List[Dict[str, Any]]:
        """
        List all resources.
        """
        ...


class AbstractIntegrationBaseService(IntegrationServiceProtocol):
    """
    Base abstract class for all integration services.
    Any integration service should inherit from this class and implement its methods.
    """

    def set_provider_data(self, provider_name: str, token_url: str, scopes: str):
        self.provider_name = provider_name
        self.token_url = token_url
        self.scopes = scopes

    async def refresh_integration_token(self, user_id: int) -> TokenData:
        """
        Refresh the access token using the refresh token.

        Returns:
            Updated TokenData if successful, None otherwise
        """
        refresh_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "scope": self.scopes,
        }
        return await self.refresh_token(self.token_url, refresh_data, user_id)

    async def get_integration_token_data(self, code: str) -> TokenData:
        """
        Exchange authorization code for token data.

        Args:
            code: The authorization code from OAuth callback

        Returns:
            TokenData object with access_token, refresh_token and expires_in
        """
        token_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_url,
            "grant_type": "authorization_code",
            "scope": self.scopes,
        }

        return await self.get_token_data(self.token_url, token_data)

    async def get_token_data(self, token_url: str, token_data: Dict) -> TokenData:
        """
        Exchange authorization code for token data.

        Args:
            code: The authorization code from OAuth callback

        Returns:
            TokenData object with access_token, refresh_token and expires_in
        """
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)
            token_response.raise_for_status()
            token = token_response.json()

        expires_in = token.get("expires_in", 3600)
        expires_at = datetime.now(UTC) + timedelta(seconds=expires_in)

        return TokenData(
            access_token=token.get("access_token"),
            refresh_token=token.get("refresh_token"),
            expires_at=expires_at,
        )

    async def _verify_access_token(
        self, token_data: TokenData, user_id: int
    ) -> TokenData:
        """
        Verify the access token and refresh it if it's close to expiration.

        Args:
            token_data: The token data to verify

        Returns:
            TokenData object - either the original if valid or a refreshed one
        """
        current_time = datetime.now(UTC)
        buffer_minutes = 5
        expiration_buffer = current_time + timedelta(minutes=buffer_minutes)

        # Ensure token_data.expires_at is also timezone-aware
        if token_data.expires_at.tzinfo is None:
            token_data.expires_at = token_data.expires_at.replace(tzinfo=UTC)

        if token_data.expires_at <= expiration_buffer:
            return await self.refresh_integration_token(user_id)

        return token_data

    async def get_integration_tokens(self, user_id: int) -> TokenData:
        """
        Get the integration tokens.
        """
        result = await self.get_query_by_user_id(user_id)

        access_token = (
            result.get("access_token")
            if isinstance(result, dict)
            else result.access_token
        )
        refresh_token = (
            result.get("refresh_token")
            if isinstance(result, dict)
            else result.refresh_token
        )
        expires_at = (
            result.get("expires_at") if isinstance(result, dict) else result.expires_at
        )

        tokens = TokenData(
            access_token=self.encryption.decrypt_token(access_token),
            refresh_token=self.encryption.decrypt_token(refresh_token),
            expires_at=expires_at,
        )

        return await self._verify_access_token(tokens, user_id)
