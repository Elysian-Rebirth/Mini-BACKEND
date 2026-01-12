from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import create_db_and_tables
from routers import flow, auth, component, variable, chat, web, base
import time
from collections import defaultdict

# Simple Memory-based Rate Limiter
RATE_LIMIT = 60  # requests per minute
RATE_WINDOW = 60 # seconds
request_counts = defaultdict(list)

def rate_limiter_middleware(request: Request):
    client_ip = request.client.host
    now = time.time()
    
    # Filter out timestamps older than window
    request_counts[client_ip] = [t for t in request_counts[client_ip] if now - t < RATE_WINDOW]
    
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
    
    request_counts[client_ip].append(now)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def add_rate_limit(request: Request, call_next):
    # Exclude OPTIONS (CORS preflight) and Health check
    if request.method != "OPTIONS" and request.url.path != "/health":
         try:
            rate_limiter_middleware(request)
         except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
            
    response = await call_next(request)
    return response

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "*" # For dev
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/user", tags=["User"])
app.include_router(flow.router, prefix="/api/v1/flows", tags=["Flow"])
app.include_router(component.router, prefix="/api/v1/component", tags=["Component"])
app.include_router(variable.router, prefix="/api/v1/variable", tags=["Variable"])
app.include_router(chat.router, prefix="/api/v1/workflow", tags=["Chat"])
app.include_router(web.router, prefix="/api/v1/web", tags=["Web"])
app.include_router(base.router, prefix="/api/v1", tags=["Base"])


@app.get("/")
def read_root():
    return {"status": "Bisheng Lite Backend is Running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
