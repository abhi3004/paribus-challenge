import httpx

class HospitalDirectoryClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def create_hospital(self, payload: dict):
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{self.base_url}/hospitals/",
                json=payload
            )
            response.raise_for_status()
            return response.json()

    async def activate_batch(self, batch_id: str):
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.patch(
                f"{self.base_url}/hospitals/batch/{batch_id}/activate"
            )
            response.raise_for_status()
            return response.json()

    async def delete_batch(self, batch_id: str):
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.delete(
                f"{self.base_url}/hospitals/batch/{batch_id}"
            )
            response.raise_for_status()
            return response.json()