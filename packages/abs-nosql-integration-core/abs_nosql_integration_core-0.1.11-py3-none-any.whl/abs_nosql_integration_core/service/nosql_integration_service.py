from typing import Dict, Optional, List
from abs_nosql_integration_core.schema import TokenData, CreateIntegration, UpdateIntegration
from abs_nosql_integration_core.repository import IntegrationRepository
from abs_exception_core.exceptions import NotFoundError
from abs_nosql_integration_core.utils import Encryption
from abs_nosql_integration_core.schema.integration_schema import Integration
from abs_nosql_repository_core.service import BaseService
from abs_integration_core.service import AbstractIntegrationBaseService
from datetime import datetime, timedelta, UTC
import httpx
from abs_nosql_repository_core.schema.base_schema import ListFilter, FilterSchema


class IntegrationBaseService(BaseService, AbstractIntegrationBaseService):
    """
    Base class for all NoSQL integration services.
    Implements the IntegrationBaseService interface with NoSQL storage.
    """
    def __init__(
        self, 
        provider_name: str, 
        integration_repository: IntegrationRepository,
        encryption: Encryption
    ):
        self.provider_name = provider_name
        self.encryption = encryption
        super().__init__(integration_repository)

    async def handle_oauth_callback(self, code: str, user_id: int) -> TokenData:
        """
        Handle the OAuth callback and store tokens.
        
        Args:
            code: The authorization code from OAuth callback
            
        Returns:
            TokenData object
        """
        token_data = await self.get_integration_token_data(code)

        try:
            # Try to update existing integration
            existing_integration = await self.get_query_by_user_id(user_id)

            # Update the integration with encrypted tokens
            update_data = UpdateIntegration(
                access_token=self.encryption.encrypt_token(token_data.access_token),
                refresh_token=self.encryption.encrypt_token(token_data.refresh_token),
                expires_at=token_data.expires_at
            )
            await self.repository.update(
                existing_integration["_id"],
                update_data.model_dump(exclude_none=True)
            )

        except NotFoundError:
            # Only create a new one if it truly doesn't exist
            create_data = CreateIntegration(
                provider_name=self.provider_name,
                access_token=self.encryption.encrypt_token(token_data.access_token),
                refresh_token=self.encryption.encrypt_token(token_data.refresh_token),
                expires_at=token_data.expires_at,
                user_id=user_id
            )
            await self.repository.create_integration(create_data)

        # Return unencrypted token data to the caller
        return token_data

    async def refresh_token(self, token_url: str, refresh_data: Dict, user_id: int) -> Optional[TokenData]:
        """
        Refresh the access token using the refresh token.
        
        Returns:
            Updated TokenData if successful, None otherwise
        """
        # Get the current integration
        integration = await self.get_query_by_user_id(user_id)
        
        # Decrypt the refresh token for use with the API
        decrypted_refresh_token = self.encryption.decrypt_token(integration["refresh_token"])
        
        # Use the refresh token to get a new access token
        refresh_data["refresh_token"] = decrypted_refresh_token

        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=refresh_data)
            token_response.raise_for_status()
            token = token_response.json()

        new_access_token = token.get("access_token")
        new_refresh_token = token.get("refresh_token", decrypted_refresh_token)
        expires_in = token.get("expires_in", 3600)
        expires_at = datetime.now(UTC) + timedelta(seconds=expires_in)
            
        # Update the integration in the database with encrypted tokens
        token_data = TokenData(
            access_token=self.encryption.encrypt_token(new_access_token),
            refresh_token=self.encryption.encrypt_token(new_refresh_token),
            expires_at=expires_at
        )
        await self.repository.refresh_token(
            integration_id=integration["_id"],
            token_data=token_data
        )
        
        # Return decrypted token data to the caller
        return TokenData(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_at=expires_at
        )

    async def get_query_by_user_id(self, user_id: int):
        find_query = FilterSchema(
                operator="and",
                conditions=[
                    {"field": "user_id", "operator": "eq", "value": user_id},
                    {"field": "provider_name", "operator": "eq", "value": self.provider_name}
                ]
            )
        query = await super().get_all(find=ListFilter(filters=find_query))
        if len(query["founds"]) > 0:
            return query["founds"][0]
        else:
            raise NotFoundError(detail="Integration not found")

    async def get_integration(self, user_id: int) -> Optional[TokenData]:
        """
        Get integration data.
        
        Returns:
            TokenData if integration exists, None otherwise
        """
        try:
            integration = await self.get_query_by_user_id(user_id)
            return integration
        except Exception:
            return None

    async def get_all_integrations(self, user_id: int) -> List[Integration]:
        """
        Get all integrations.
        
        Returns:
            List of TokenData objects
        """
        try:
            integrations = await super().get_all(schema=ListFilter())
            return integrations
        except Exception:
            return []

    async def delete_integration(self, user_id: int) -> bool:
        """
        Delete an integration.
        
        Returns:
            True if deleted, False otherwise
        """
        try:
            integration = await self.get_query_by_user_id(user_id)
            await super().delete(integration["_id"])

            return True

        except NotFoundError:
            # If the integration doesn't exist, consider it "deleted"
            return True

        except Exception as e:
            print(f"Error deleting integration: {str(e)}")
            return False
