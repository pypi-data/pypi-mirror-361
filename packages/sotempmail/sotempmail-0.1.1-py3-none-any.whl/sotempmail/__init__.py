import aiohttp
from typing import List


class TempMailSo:
    url = "https://tempmail-so.p.rapidapi.com"

    def __init__(self, rapid_api_key: str, token_bearer: str):
        self.rapid_api_key = rapid_api_key
        self.token_bearer = token_bearer

    def __headers(self) -> dict[str, str]:
        return {
            "X-RapidAPI-Host": "tempmail-so.p.rapidapi.com",
            "X-RapidAPI-Key": self.rapid_api_key,
            "Authorization": f"Bearer {self.token_bearer}",
        }
    
    async def create_inbox(self, name: str, domain: str, lifespan: int) -> str:
        async with aiohttp.ClientSession(headers=self.__headers()) as cli:
            headers = self.__headers()
            headers["Content-Type"] = "application/json"
            payload = {
                "name": name,
                "domain": domain
            }
            url = self.url + "/inboxes"
            async with cli.post(url, headers=headers, json=payload) as resp:
                data = await resp.json()
                if data is None:
                    raise Exception("Failed to create inbox")
                elif data.get("code") != 0:
                    raise Exception(data.get("message"))
                return data.get("data")
    
    async def delete_email(self, inbox_id: str, email_id: str) -> None:
        async with aiohttp.ClientSession(headers=self.__headers()) as cli:
            headers = self.__headers()
            headers["Content-Type"] = "application/json"
            payload = {}
            url = self.url + f"/inboxes/{inbox_id}/mails/{email_id}"
            async with cli.delete(url, headers=headers, json=payload) as resp:
                data = await resp.json()
                if data is None:
                    raise Exception("Failed to delete email")
                elif data.get("code") != 0:
                    raise Exception(data.get("message"))
    
    async def delete_inbox(self, inbox_id: str) -> None:
        async with aiohttp.ClientSession(headers=self.__headers()) as cli:
            headers = self.__headers()
            headers["Content-Type"] = "application/json"
            payload = {}
            url = self.url + f"/inboxes/{inbox_id}"
            async with cli.delete(url, headers=headers, json=payload) as resp:
                data = await resp.json()
                if data is None:
                    raise Exception("Failed to delete inbox")
                elif data.get("code") != 0:
                    raise Exception(data.get("message"))
    
    async def list_domains(self) -> List[str]:
        async with aiohttp.ClientSession(headers=self.__headers()) as cli:
            headers = self.__headers()
            url = self.url + "/domains"
            async with cli.get(url, headers=headers) as resp:
                data = await resp.json()
                if data is None:
                    raise Exception("Failed to get domains")
                elif data.get("code") != 0:
                    raise Exception(data.get("message"))
                return data.get("data")
    
    async def list_emails(self, inbox_id: str) -> List[dict[str, str]]:
        async with aiohttp.ClientSession(headers=self.__headers()) as cli:
            headers = self.__headers()
            url = self.url + f"/inboxes/{inbox_id}/mails"
            async with cli.get(url, headers=headers) as resp:
                data = await resp.json()
                if data is None:
                    raise Exception("Failed to get emails")
                elif data.get("code") != 0:
                    raise Exception(data.get("message"))
                return data.get("data")
    
    async def list_inboxes(self) -> List[dict[str, str]]:
        async with aiohttp.ClientSession(headers=self.__headers()) as cli:
            headers = self.__headers()
            url = self.url + "/inboxes"
            async with cli.get(url, headers=headers) as resp:
                data = await resp.json()
                if data is None:
                    raise Exception("Failed to get inboxes")
                elif data.get("code") != 0:
                    raise Exception(data.get("message"))
                return data.get("data")
    
    async def retrieve_email(self, inbox_id: str, email_id: str) -> dict[str, str]:
        async with aiohttp.ClientSession(headers=self.__headers()) as cli:
            headers = self.__headers()
            url = self.url + f"/inboxes/{inbox_id}/mails/{email_id}"
            async with cli.get(url, headers=headers) as resp:
                data = await resp.json()
                if data is None:
                    raise Exception("Failed to get email")
                elif data.get("code") != 0:
                    raise Exception(data.get("message"))
                return data.get("data")