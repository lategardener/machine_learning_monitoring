from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from routes import gateway
from config import API_KEY
from fastapi.middleware.cors import CORSMiddleware
from middleware.rate_limit import RateLimiter

app = FastAPI()
app.include_router(gateway.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)
    
    excluded_paths = ["/docs", "/openapi.json", "/redoc"]
    if request.url.path in excluded_paths:
        return await call_next(request)

    api_key = request.headers.get("X-API-KEY")
    if not api_key or api_key.lower() != API_KEY.lower():
        return JSONResponse(
            status_code=401,
            content={"detail": "Unauthorized: invalid API key"}
        )

    return await call_next(request)

rate_limiter = RateLimiter(interval_seconds=20)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)
    
    excluded_paths = ["/docs", "/openapi.json", "/redoc"]
    if request.url.path in excluded_paths:
        return await call_next(request)

    client_ip = request.client.host
    if not rate_limiter.is_allowed(client_ip):
        return JSONResponse(
            status_code=429,
            content={"detail": "Too Many Requests: wait 20 seconds before retrying"}
        )

    return await call_next(request)