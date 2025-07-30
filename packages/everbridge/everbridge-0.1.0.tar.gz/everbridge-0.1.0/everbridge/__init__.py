import aiohttp

from .models import Notification, AccessTokenResponse

BASE_URL = "https://api.everbridge.net/digitalapps/v2"


class EverbridgeClient:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.refresh_token = None
        self.access_token = None
        self.expires_at = None

    async def get_access_token(self) -> AccessTokenResponse:
        """Get access token using username and password"""
        url = f"{BASE_URL}/authorizations/oauth2/token"

        headers = {
            "accept": "application/json",
        }

        payload = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload) as response:
                r_json = await response.json()

        return AccessTokenResponse(**r_json)

    async def get_notifications(self) -> list[Notification]:
        """Get all notifications"""
        token_response = await self.get_access_token()

        url = f"{BASE_URL}/notifications/messages"

        headers = {
            "accept": "application/json",
            "Authorization": f"token {token_response.accessToken.value}",
            "Client-Id": token_response.clientId,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                r_json = await response.json()

        notifications = [Notification(**item) for item in r_json]

        return notifications

    async def get_notification(self, notification_id: str) -> Notification:
        """Get a single notification by its ID"""
        token_response = await self.get_access_token()

        url = f"{BASE_URL}/notifications/messages/{notification_id}"

        headers = {
            "accept": "application/json",
            "Authorization": f"token {token_response.accessToken.value}",
            "Client-Id": token_response.clientId,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                r_json = await response.json()

        notification = Notification(**r_json)

        return notification
