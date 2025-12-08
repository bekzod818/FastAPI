from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
from typing import Optional
import logging
from datetime import datetime
import jwt
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ShopMicro API Gateway",
    description="Central API Gateway for E-Commerce Microservices",
    version="1.0.0",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service Registry - In production, use service discovery like Consul/Eureka
SERVICE_REGISTRY = {
    "user": "http://user-service:8001",
    "product": "http://product-service:8002",
    "order": "http://order-service:8003",
    "payment": "http://payment-service:8004",
    "notification": "http://notification-service:8005",
    "inventory": "http://inventory-service:8006",
}

# Secret key for JWT validation (should be in environment variables)
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"


class RateLimiter:
    """Simple in-memory rate limiter - use Redis in production"""

    def __init__(self):
        self.requests = {}

    def check_rate_limit(self, client_ip: str, limit: int = 100) -> bool:
        current_time = datetime.now()
        if client_ip not in self.requests:
            self.requests[client_ip] = []

        # Remove requests older than 1 minute
        self.requests[client_ip] = [
            req_time
            for req_time in self.requests[client_ip]
            if (current_time - req_time).seconds < 60
        ]

        if len(self.requests[client_ip]) >= limit:
            return False

        self.requests[client_ip].append(current_time)
        return True


rate_limiter = RateLimiter()


# Middleware for logging and rate limiting
@app.middleware("http")
async def gateway_middleware(request: Request, call_next):
    # Rate limiting
    client_ip = request.client.host
    if not rate_limiter.check_rate_limit(client_ip):
        return JSONResponse(status_code=429, content={"detail": "Too many requests"})

    # Log request
    logger.info(f"Request: {request.method} {request.url.path} from {client_ip}")

    # Process request
    start_time = datetime.now()
    response = await call_next(request)
    process_time = (datetime.now() - start_time).total_seconds()

    # Log response
    logger.info(f"Response: {response.status_code} - Time: {process_time}s")

    response.headers["X-Process-Time"] = str(process_time)
    return response


async def verify_token(request: Request) -> Optional[dict]:
    """Verify JWT token from Authorization header"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def proxy_request(
    service_name: str,
    path: str,
    method: str,
    request: Request,
    require_auth: bool = False,
):
    """Proxy request to appropriate microservice"""

    # Authentication check
    user_data = None
    if require_auth:
        user_data = await verify_token(request)
        if not user_data:
            raise HTTPException(status_code=401, detail="Authentication required")

    # Get service URL
    service_url = SERVICE_REGISTRY.get(service_name)
    if not service_url:
        raise HTTPException(status_code=404, detail=f"Service {service_name} not found")

    # Prepare request
    url = f"{service_url}{path}"
    headers = dict(request.headers)
    headers.pop("host", None)  # Remove host header

    # Add user context to headers
    if user_data:
        headers["X-User-ID"] = str(user_data.get("user_id"))
        headers["X-User-Email"] = user_data.get("email", "")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get request body
            body = await request.body() if method in ["POST", "PUT", "PATCH"] else None

            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                params=request.query_params,
                content=body,
            )

            return JSONResponse(
                content=response.json() if response.text else {},
                status_code=response.status_code,
            )
    except httpx.TimeoutException:
        logger.error(f"Timeout calling {service_name} service")
        raise HTTPException(status_code=504, detail="Service timeout")
    except httpx.RequestError as e:
        logger.error(f"Error calling {service_name} service: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Check health of API Gateway and all services"""
    service_health = {}

    async with httpx.AsyncClient(timeout=5.0) as client:
        for service_name, service_url in SERVICE_REGISTRY.items():
            try:
                response = await client.get(f"{service_url}/health")
                service_health[service_name] = (
                    "healthy" if response.status_code == 200 else "unhealthy"
                )
            except:
                service_health[service_name] = "unreachable"

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": service_health,
    }


# ===== USER SERVICE ROUTES =====
@app.post("/api/users/register")
async def register_user(request: Request):
    return await proxy_request("user", "/users/register", "POST", request)


@app.post("/api/users/login")
async def login_user(request: Request):
    return await proxy_request("user", "/users/login", "POST", request)


@app.get("/api/users/me")
async def get_current_user(request: Request):
    return await proxy_request("user", "/users/me", "GET", request, require_auth=True)


@app.get("/api/users/{user_id}")
async def get_user(user_id: int, request: Request):
    return await proxy_request(
        "user", f"/users/{user_id}", "GET", request, require_auth=True
    )


# ===== PRODUCT SERVICE ROUTES =====
@app.get("/api/products")
async def list_products(request: Request):
    return await proxy_request("product", "/products", "GET", request)


@app.get("/api/products/{product_id}")
async def get_product(product_id: int, request: Request):
    return await proxy_request("product", f"/products/{product_id}", "GET", request)


@app.post("/api/products")
async def create_product(request: Request):
    return await proxy_request(
        "product", "/products", "POST", request, require_auth=True
    )


@app.put("/api/products/{product_id}")
async def update_product(product_id: int, request: Request):
    return await proxy_request(
        "product", f"/products/{product_id}", "PUT", request, require_auth=True
    )


# ===== ORDER SERVICE ROUTES =====
@app.get("/api/orders")
async def list_orders(request: Request):
    return await proxy_request("order", "/orders", "GET", request, require_auth=True)


@app.post("/api/orders")
async def create_order(request: Request):
    return await proxy_request("order", "/orders", "POST", request, require_auth=True)


@app.get("/api/orders/{order_id}")
async def get_order(order_id: int, request: Request):
    return await proxy_request(
        "order", f"/orders/{order_id}", "GET", request, require_auth=True
    )


# ===== PAYMENT SERVICE ROUTES =====
@app.post("/api/payments")
async def create_payment(request: Request):
    return await proxy_request(
        "payment", "/payments", "POST", request, require_auth=True
    )


@app.get("/api/payments/{payment_id}")
async def get_payment(payment_id: int, request: Request):
    return await proxy_request(
        "payment", f"/payments/{payment_id}", "GET", request, require_auth=True
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
