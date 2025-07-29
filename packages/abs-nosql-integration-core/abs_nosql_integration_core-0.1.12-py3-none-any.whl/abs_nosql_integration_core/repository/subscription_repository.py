from abs_nosql_integration_core.model import SubscriptionDocument
from abs_nosql_integration_core.schema.subscription_schema import Subscription as SubscriptionSchema
from abs_nosql_repository_core.repository.base_repository import BaseRepository
from abs_nosql_repository_core.schema import ListFilter
from typing import List


class SubscriptionsRepository(BaseRepository):
    def __init__(self):
        super().__init__(SubscriptionDocument)

    async def create(self, schema: SubscriptionSchema, collection_name: str = None) -> dict:
        subscription = SubscriptionSchema(
            **schema.model_dump()
        )
        return await super().create(subscription, collection_name)
    
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
        list_filter = ListFilter(
            filters={
                "operator": "and",
                "conditions": [
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
            },
            page=page,
            page_size=page_size
        )
        
        # Get all subscriptions for the provider
        result = await self.get_all(list_filter)
        
        # Convert the found documents to SubscriptionSchema objects
        # subscriptions = []
        # for subscription in result["founds"]:
        #     subscriptions.append(SubscriptionSchema(**subscription))
            
        return result
