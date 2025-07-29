from abs_integration_core.repository import SubscriptionsRepository
from abs_repository_core.services.base_service import BaseService
from abs_integration_core.schema import Subscription
from abs_repository_core.schemas import FilterSchema, FindBase
from typing import List
from abs_exception_core.exceptions import NotFoundError


class SubscriptionService(BaseService):
    def __init__(self, subscription_repository: SubscriptionsRepository):
        super().__init__(subscription_repository)

    async def create(self, schema: Subscription) -> Subscription:
        subscription = super().add(schema)
        return subscription

    async def remove_by_uuid(self, uuid: str) -> Subscription:
        id = self.get_by_attr("uuid", uuid).id
        return super().remove_by_id(id)

    async def list_subscriptions(self, provider_name: str, user_id: int, page: int = 1, page_size: int = 10) -> List[Subscription]:
        return await self._repository.list_subscriptions(provider_name, user_id, page, page_size)
    
    async def get_user_id_by_subscription_id(self, subscription_id: str) -> int:
        """
        Get the user ID by subscription ID.
        """
        list_filter = FilterSchema(
            operator="AND",
            conditions=[
                {
                    "field": "target_url",
                    "operator": "like",
                    "value": f"/{subscription_id}"
                }
            ]
        )

        result = super().get_list(
            schema=FindBase(
                filters=list_filter,
                page=1,
                page_size=1
            )
        )

        if result.get("founds"):
            return result["founds"][0].user_id
        else:
            raise NotFoundError("Subscription not found")
