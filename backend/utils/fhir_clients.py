import httpx
import logging
from config import settings

logger = logging.getLogger("doctor_zenz.fhir")


class FHIRClient:

    def __init__(self):
        self.base_url = settings.FHIR_BASE_URL
        self.headers  = {
            "Content-Type": "application/fhir+json",
            "Accept"      : "application/fhir+json"
        }

    async def create_resource(self, resource_type: str, resource_data: dict) -> dict:
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/{resource_type}",
                json=resource_data,
                headers=self.headers,
                timeout=30.0
            )

            if response.status_code not in (200, 201):
                logger.error(f"FHIR error creating {resource_type}: {response.text}")
                raise Exception(f"FHIR server rejected {resource_type}: {response.status_code}")

            return response.json()

    async def get_resource(self, resource_type: str, resource_id: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/{resource_type}/{resource_id}",
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()


fhir_client = FHIRClient()