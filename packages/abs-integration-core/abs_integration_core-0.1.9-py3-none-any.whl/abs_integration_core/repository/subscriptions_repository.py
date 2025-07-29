from abs_integration_core.models import Subscription
from abs_integration_core.schema import Subscription as SubscriptionSchema
from typing import Callable
from sqlalchemy.orm import Session
from abs_repository_core.repository import BaseRepository
from typing import List
from abs_repository_core.schemas.base_schema import FilterSchema, FindBase


class SubscriptionsRepository(BaseRepository):
    def __init__(self, db: Callable[..., Session]):
        super().__init__(db, Subscription)
        
    
    def create(self, schema: SubscriptionSchema) -> Subscription:
        subscription = Subscription(
            **schema.model_dump()
        )
        return super().create(subscription)

    async def list_subscriptions(
        self,
        provider_name: str,
        user_id: int,
        page: int = 1,
        page_size: int = 10,
    ) -> List[SubscriptionSchema]:
        """
        List all subscriptions for a specific provider.
        
        Args:
            provider_name: The name of the provider to list subscriptions for
            
        Returns:
            List of subscription objects
        """
        # Create a ListFilter with the provider_name filter
        list_filter = FilterSchema(
            operator="AND",
            conditions=[
                {
                    "field": "provider_name",
                        "operator": "eq",
                        "value": provider_name
                    },
                    {
                        "field": "user_id",
                        "operator": "eq",
                        "value": user_id
                    }
                ]
        )
        
        # Get all subscriptions for the provider
        result = self.read_by_options(
            schema=FindBase(
                filters=list_filter,
                page=page,
                page_size=page_size
            )
        )
        
        # # Convert the found documents to SubscriptionSchema objects
        # subscriptions = []
        # for subscription in result["founds"]:
        #     subscriptions.append(
        #         SubscriptionSchema(
        #             uuid=subscription.uuid,
        #             resource_type=subscription.resource_type,
        #             site_id=subscription.site_id,
        #             resource_id=subscription.resource_id,
        #             change_type=subscription.change_type,
        #             provider_name=subscription.provider_name,
        #             user_id=subscription.user_id
        #         )
        #     )
            
        return result

