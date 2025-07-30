from spryx_core import NOT_GIVEN, is_given
from spryx_http import SpryxAsyncClient


class CreditCards:
    def __init__(self, client: SpryxAsyncClient):
        self._client = client
        self._base_url = client.base_url

    async def list(
        self,
        organization_id: str,
        page: int = 1,
        limit: int = 10,
        order: str = "asc",
        brand: str = NOT_GIVEN,
        country: str = NOT_GIVEN,
        last4: str = NOT_GIVEN,
    ) -> dict:
        """List credit cards for the authenticated organization."""
        params = {
            "page": page,
            "limit": limit,
            "order": order,
            "organization_id": organization_id,
        }
        
        if is_given(brand):
            params["brand"] = brand
        if is_given(country):
            params["country"] = country
        if is_given(last4):
            params["last4"] = last4

        return await self._client.get(
            f"{self._base_url}/v1/credit-cards",
            params=params,
            headers={"x-organization-id": organization_id},
        )

    async def retrieve(
        self,
        credit_card_id: str,
        organization_id: str = NOT_GIVEN,
    ) -> dict:
        """Retrieve a specific credit card by ID.
        
        The credit card must belong to the authenticated organization.
        """
        return await self._client.get(
            f"{self._base_url}/v1/credit-cards/{credit_card_id}",
            headers={"x-organization-id": organization_id} if is_given(organization_id) else None,
        )

    async def delete(
        self,
        credit_card_id: str,
        organization_id: str = NOT_GIVEN,
    ) -> dict:
        """Delete a specific credit card by ID.
        
        The credit card must belong to the authenticated organization.
        Cannot delete the default credit card for the organization.
        """
        return await self._client.delete(
            f"{self._base_url}/v1/credit-cards/{credit_card_id}",
            headers={"x-organization-id": organization_id} if is_given(organization_id) else None,
        ) 