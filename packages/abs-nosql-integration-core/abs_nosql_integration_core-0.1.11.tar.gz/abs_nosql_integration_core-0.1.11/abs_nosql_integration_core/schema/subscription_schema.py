from pydantic import Field
from typing import Optional
from datetime import datetime
from abs_nosql_repository_core.document.base_document import BaseDraftDocument


class Subscription(BaseDraftDocument):
    resource_type: Optional[str] = Field(None, description="The type of the resource")
    site_id: Optional[str] = Field(None, description="The ID of the site")
    resource_id: Optional[str] = Field(None, description="The ID of the resource")
    change_type: Optional[str] = Field(None, description="The type of change")
    provider_name: Optional[str] = Field(None, description="The name of the provider")

    user_id: Optional[int] = Field(None, description="The ID of the user")

    class Settings:
        name = "subscriptions"
