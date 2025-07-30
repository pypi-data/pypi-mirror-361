from typing import Literal

import aiohttp


class OZClient:
    def __init__(self, client_id, api_key: str, session: aiohttp.ClientSession | None = None):
        self.client_id = client_id
        self.api_key = api_key
        self.session = session or aiohttp.ClientSession(
            headers={
                "Client-Id": client_id,
                "Api-Key": api_key,
                "Content-Type": "application/json",
            }
        )

    async def close(self):
        await self.session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def get_ozon_cluster_list(
        self,
        cluster_type: Literal[
            "CLUSTER_TYPE_OZON",
            "CLUSTER_TYPE_CIS",
        ] = "CLUSTER_TYPE_OZON",
    ):
        """Получить список кластеров Ozon Seller API."""
        url = "https://api-seller.ozon.ru/v1/cluster/list"
        data = {"cluster_type": cluster_type}
        async with self.session.post(url=url, json=data) as resp:
            return await resp.json()
