from spryx_core import NOT_GIVEN, is_given
from spryx_http import SpryxAsyncClient


class Stripe:
    def __init__(self, client: SpryxAsyncClient):
        self._client = client
        self._base_url = client.base_url

    async def create_setup_intent(
        self,
        organization_id: str = NOT_GIVEN,
    ) -> dict:
        """Create a Setup Intent for collecting payment method details.
        
        Returns:
            Setup Intent response with client_secret and setup_intent_id
        """
        return await self._client.post(
            f"{self._base_url}/stripe/setup-intent",
            headers={"x-organization-id": organization_id} if is_given(organization_id) else None,
        ) 