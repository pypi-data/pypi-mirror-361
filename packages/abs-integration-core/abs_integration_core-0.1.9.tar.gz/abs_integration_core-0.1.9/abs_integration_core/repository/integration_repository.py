from abs_repository_core.repository import BaseRepository
from abs_integration_core.models import Integration
from typing import Callable
from sqlalchemy.orm import Session
from abs_integration_core.schema import CreateIntegration
from abs_integration_core.schema import TokenData

class IntegrationRepository(BaseRepository):
    def __init__(self, db: Callable[..., Session]):
        self.db = db
        super().__init__(db, Integration)
    
    def create_integration(self, integration_data: CreateIntegration) -> Integration:
        """
        Create a new integration record.
        
        Args:
            integration_data: Integration data including provider_name, access_token, etc.
            
        Returns:
            The created integration object
            
        Raises:
            DuplicatedError: If integration with same provider already exists
        """
        new_integration = Integration(
            provider_name=integration_data.provider_name,
            access_token=integration_data.access_token,
            refresh_token=integration_data.refresh_token,
            expires_at=integration_data.expires_at,
            user_id=integration_data.user_id
        )
        
        integration = super().create(new_integration)
        return integration
    
    def refresh_token(
        self,
        integration_id: int, 
        token_data: TokenData
    ) -> Integration:
        """
        Update token information for a specific integration.
        
        Args:
            provider_name: The integration provider name
            token_data: The data to update
            
        Returns:
            The updated integration object
            
        Raises:
            NotFoundError: If integration doesn't exist
        """
        integration_data = super().update(integration_id, token_data)

        return integration_data
