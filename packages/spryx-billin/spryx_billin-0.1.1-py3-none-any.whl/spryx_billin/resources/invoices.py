from spryx_core import NOT_GIVEN, is_given
from spryx_http import SpryxAsyncClient

from spryx_billin.types.billing import InvoiceStatus


class Invoices:
    def __init__(self, client: SpryxAsyncClient):
        self._client = client
        self._base_url = client.base_url

    async def list(
        self,
        organization_id: str,
        page: int = 1,
        limit: int = 10,
        order: str = "asc",
        status: InvoiceStatus = NOT_GIVEN,
        start_date: str = NOT_GIVEN,
        end_date: str = NOT_GIVEN,
    ) -> dict:
        """List invoices for the authenticated organization."""
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
            f"{self._base_url}/v1/invoices",
            params=params,
            headers={"x-organization-id": organization_id},
        ) 