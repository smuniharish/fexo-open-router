import httpx


async def check_url_valid_head(url: str, timeout: float = 5.0) -> bool:
    async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
        try:
            response = await client.head(url)
            return response.status_code < 400
        except httpx.RequestError:
            return False
