from spryx_core import NOT_GIVEN, is_given
from spryx_http import SpryxAsyncClient

from spryx_billin.types.billing import InvoiceStatus


class OrgCustomers:
    def __init__(self, client: SpryxAsyncClient):
        self._client = client
        self._base_url = client.base_url

    async def create(
        self,
        name: str,
        email: str,
        organization_id: str = NOT_GIVEN,
    ) -> dict:
        """Create a new organization customer."""
        payload = {
            "name": name,
            "email": email,
        }

        return await self._client.post(
            f"{self._base_url}/v1/org-costumers",
            json=payload,
            headers={"x-organization-id": organization_id} if is_given(organization_id) else None,
        )

    async def get(
        self,
        organization_id: str = NOT_GIVEN,
    ) -> dict:
        """Get organization customer."""
        return await self._client.get(
            f"{self._base_url}/v1/org-costumers",
            headers={"x-organization-id": organization_id} if is_given(organization_id) else None,
        )

    async def update_default_credit_card(
        self,
        credit_card_id: str,
        organization_id: str = NOT_GIVEN,
    ) -> dict:
        """Update default credit card for the organization customer."""
        payload = {
            "credit_card_id": credit_card_id,
        }

        return await self._client.put(
            f"{self._base_url}/v1/org-costumers/default-credit-card",
            json=payload,
            headers={"x-organization-id": organization_id} if is_given(organization_id) else None,
        )

    async def list_invoices(
        self,
        organization_id: str,
        page: int = 1,
        limit: int = 10,
        order: str = "asc",
        status: InvoiceStatus = NOT_GIVEN,
        start_date: str = NOT_GIVEN,
        end_date: str = NOT_GIVEN,
    ) -> dict:
        """List invoices for the organization customer."""
        params = {
            "page": page,
            "limit": limit,
            "order": order,
            "organization_id": organization_id,
        }
        
        if is_given(status):
            params["status"] = status.value
        if is_given(start_date):
            params["start_date"] = start_date
        if is_given(end_date):
            params["end_date"] = end_date

        return await self._client.get(
            f"{self._base_url}/v1/org-costumers/invoices",
            params=params,
            headers={"x-organization-id": organization_id},
        ) 