from abs_nosql_integration_core.repository import SubscriptionsRepository
from abs_nosql_repository_core.service.base_service import BaseService
from abs_nosql_integration_core.schema import Subscription
from typing import List
from abs_nosql_repository_core.schema.base_schema import FilterSchema, LogicalOperator, FieldOperatorCondition, Operator, ListFilter
from abs_exception_core.exceptions import NotFoundError

class SubscriptionService(BaseService):
    def __init__(self, subscription_repository: SubscriptionsRepository):
        super().__init__(subscription_repository)

    async def create(self, schema: Subscription, collection_name: str = None) -> Subscription:
        return await self.repository.create(schema, collection_name)

    async def remove_by_uuid(self, uuid: str) -> Subscription:
        existing_subscription = await self.get_by_attr("uuid", uuid)
        return await super().delete(existing_subscription["id"])
    
    async def list_subscriptions(self, provider_name: str, user_id: int, page: int = 1, page_size: int = 10) -> List[Subscription]:
        return await self.repository.list_subscriptions(provider_name, user_id, page, page_size)
    
    async def get_user_id_by_subscription_id(self, subscription_id: str) -> int:
        """
        Get the user ID by subscription ID.
        """
        find_query = FilterSchema(
            operator=LogicalOperator.AND,
            conditions=[
                FieldOperatorCondition(
                    field="target_url",
                    operator=Operator.LIKE,
                    value=f".*/{subscription_id}"
                )
            ]
        )

        db_records = await self.get_all(find=ListFilter(filters=find_query, page=1, page_size=1))
        if db_records.get("founds"):
            return db_records["founds"][0]["user_id"]
        else:
            raise NotFoundError("Subscription not found")
