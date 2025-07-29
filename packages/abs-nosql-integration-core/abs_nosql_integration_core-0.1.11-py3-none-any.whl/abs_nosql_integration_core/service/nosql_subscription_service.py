from abs_nosql_integration_core.repository import SubscriptionsRepository
from abs_nosql_repository_core.service.base_service import BaseService
from abs_nosql_integration_core.schema import Subscription
from typing import List


class SubscriptionService(BaseService):
    def __init__(self, subscription_repository: SubscriptionsRepository):
        super().__init__(subscription_repository)

    async def create(self, schema: Subscription) -> Subscription:
        return await super().create(schema)

    async def remove_by_uuid(self, uuid: str) -> Subscription:
        existing_subscription = await self.get_by_attr("uuid", uuid)
        return await super().delete(existing_subscription["id"])
    
    async def list_subscriptions(self, provider_name: str, user_id: int, page: int = 1, page_size: int = 10) -> List[Subscription]:
        return await self.repository.list_subscriptions(provider_name, user_id, page, page_size)
