from backend.core.config import settings
import httpx

API_KEY = settings.NUM_API_KEY
_client = None


async def get_client():
    """
    Returns a shared AsyncClient instance for connection pooling.
    For low-traffic use, a context manager is sufficient.
    """
    global _client
    if _client is None:
        _client = httpx.AsyncClient()

    return _client


async def close_client():
    """
    Function for closing client connection while app shuts down.
    """
    global _client
    if _client:
        await _client.aclose()
        _client = None


async def check_number(number: str) -> dict:
    URL = f"https://apilayer.net/api/validate?access_key={API_KEY}&number={number}"
    try:
        client = await get_client()
        response = await client.get(URL, timeout=10)
        response.raise_for_status()
        return response.json()

    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP Error: {e.response.status_code}"}
    except httpx.HTTPError:
        return {"error": "Connection error"}


