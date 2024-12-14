from functools import cache
import aiohttp

class BlandServiceError(Exception):
    pass


class BlandService:
    api_key: str
    pathway_id: str | None
    start: str | None
    voice_id: str | None

    def __init__(self, api_key: str, pathway_id: str | None, voice_id: str | None, start_node_id: str | None = None) -> None:
        self.api_key = api_key
        self.pathway_id = pathway_id
        self.voice_id = voice_id
        self.start = start_node_id
    
    @property
    @cache
    def calls(self) -> "BlandCallService":
        return BlandCallService(self.api_key, self.pathway_id, self.voice_id, self.start)


    async def _send_post_request(self, url: str, data: dict, aiohttp_session: aiohttp.ClientSession, headers: dict = {}) -> dict:
        if headers:
            headers.update({"authorization": self.api_key, "Content-Type": "application/json"})
        else:
            headers = {"authorization": self.api_key, "Content-Type": "application/json"}
        
        async with aiohttp_session.post(url, headers=headers, json=data) as response:
            return await response.json()

    async def _send_get_request(self, url: str, aiohttp_session: aiohttp.ClientSession) -> dict:
        headers = {
            "authorization": self.api_key,
        }
        async with aiohttp_session.get(url, headers=headers) as response:  # type: ignore
            return await response.json()
    

class BlandCallService(BlandService):
    api_key: str
    pathway_id: str | None
    start: str | None
    voice_id: str | None

    def __init__(self, api_key: str, pathway_id: str | None, voice_id: str | None, start_node_id: str | None = None) -> None:
        self.api_key = api_key
        self.pathway_id = pathway_id
        self.voice_id = voice_id
        self.start = start_node_id

    async def send_call(self, number: str, aiohttp_session: aiohttp.ClientSession) -> dict:
        url = "https://api.bland.ai/v1/calls"
        data = {"phone_number": number, "pathway_id": self.pathway_id}
        if self.start:
            data["start_node_id"] = self.start
        if self.voice_id:
            data["voice"] = self.voice_id
        return await self._send_post_request(url, data, aiohttp_session)

    async def stop_call(self, call_id: str, aiohttp_session: aiohttp.ClientSession) -> dict:
        url = f"https://api.bland.ai/v1/calls/{call_id}/stop"
        return await self._send_post_request(url, {}, aiohttp_session)

    async def stop_all_active_calls(self, aiohttp_session: aiohttp.ClientSession) -> dict:
        url = "https://api.bland.ai/v1/calls/active/stop"
        return await self._send_post_request(url, {}, aiohttp_session)

    async def get_call_details(self, call_id: str, aiohttp_session: aiohttp.ClientSession):
        url = f"https://api.bland.ai/v1/calls/{call_id}"
        return await self._send_get_request(url, aiohttp_session)
    
    async def list_calls(self, aiohttp_session: aiohttp.ClientSession) -> dict:
        url = "https://api.bland.ai/v1/calls"
        return await self._send_get_request(url, aiohttp_session)

    async def get_call_recording(self, call_id: str, aiohttp_session: aiohttp.ClientSession) -> dict:
        url = f"https://api.bland.ai/v1/calls/{call_id}/recording"
        return await self._send_get_request(url, aiohttp_session)

    async def get_call_transcript(self, call_id: str, aiohttp_session: aiohttp.ClientSession) -> dict:
        url = f"https://api.bland.ai/v1/calls/{call_id}/correct"
        return await self._send_get_request(url, aiohttp_session)    

    async def get_event_stream(self, aiohttp_session: aiohttp.ClientSession) -> dict:
        url = "https://api.bland.ai/v1/calls/events"
        return await self._send_get_request(url, aiohttp_session)
