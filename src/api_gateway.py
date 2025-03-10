from fastapi import FastAPI, HTTPException, Request, Depends
import httpx
from loguru import logger
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from contextlib import asynccontextmanager

from config import Config
from clients import RedisClient


async def forward_request(url: str, body):
    """Forward request to the backend microservice and cache response."""
    async with httpx.AsyncClient() as client:
        try:
            cache_key = f"{url}-post"
            
            redis = await RedisClient().get_redis()
            cached_response = await redis.get(cache_key)
            if cached_response:
                logger.info("Returning cached response")
                return cached_response.decode("utf-8")

            response = await client.request(
                method="post",
                url=url,
                json=body,
                timeout=10
            )
            
            if response.status_code == 200:
                await redis.set(cache_key, response.text, ex=60)  # Cache for 60 sec
            
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Error {e.response.status_code}: {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            logger.error(f"Service unreachable: {str(e)}")
            raise HTTPException(status_code=500, detail="Service unavailable")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    redis = await RedisClient().get_redis()
    await FastAPILimiter.init(redis)
    yield

app = FastAPI(title="API Gateway with Caching & Rate Limiting", lifespan=lifespan)


@app.post("/ask", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def ask(request: Request):
    """AI-driven query endpoint (rate limited: 5 requests/min)."""
    body = await request.json()
    url = None
    if "financials" in body:
        request = body["financials"]
        url = f"{Config.DATA_STORAGE_QUERY_SERVICE_URL}/query/financials"
    elif "news" in body:
        request = body["news"]
        url = f"{Config.DATA_STORAGE_QUERY_SERVICE_URL}/query/news"
    return await forward_request(url, request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
