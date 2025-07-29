from abs_nosql_repository_core.document.base_document import BaseDraftDocument
from pydantic import Field


class SubscriptionDocument(BaseDraftDocument):
    resource_type: str = Field(..., description="The type of the resource")
    site_id: str = Field(..., description="The ID of the site")
    resource_id: str = Field(..., description="The ID of the resource")
    change_type: str = Field(..., description="The type of change")
    provider_name: str = Field(..., description="The name of the provider")

    user_id: int = Field(..., description="The ID of the user")

    class Settings:
        name = "subscriptions"
