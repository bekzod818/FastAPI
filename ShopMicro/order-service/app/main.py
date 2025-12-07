from fastapi import FastAPI, HTTPException, Depends, Header, status
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Float,
    ForeignKey,
    Enum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import httpx
import asyncio
import json
import os
import enum

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://user:password@order-db:5432/orderdb"
)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Service URLs
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8002")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://payment-service:8004")
INVENTORY_SERVICE_URL = os.getenv(
    "INVENTORY_SERVICE_URL", "http://inventory-service:8006"
)
NOTIFICATION_SERVICE_URL = os.getenv(
    "NOTIFICATION_SERVICE_URL", "http://notification-service:8005"
)

app = FastAPI(
    title="Order Service", description="Order management microservice", version="1.0.0"
)


# ===== ENUMS =====
class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


# ===== DATABASE MODELS =====
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    total_amount = Column(Float, nullable=False)
    status = Column(String, default=OrderStatus.PENDING.value)
    payment_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")


# Create tables
Base.metadata.create_all(bind=engine)


# ===== PYDANTIC SCHEMAS =====
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]


class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_amount: float
    status: str
    payment_id: Optional[int]
    items: List[OrderItemResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== DEPENDENCIES =====
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user_id(x_user_id: Optional[str] = Header(None)) -> int:
    """Extract user ID from header set by API Gateway"""
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in request",
        )
    return int(x_user_id)


# ===== UTILITY FUNCTIONS =====
async def get_product_price(product_id: int) -> float:
    """Call Product Service to get product price"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}")
            if response.status_code == 200:
                product = response.json()
                return product["price"]
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product {product_id} not found",
                )
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Product service unavailable",
            )


async def check_inventory(product_id: int, quantity: int) -> bool:
    """Call Inventory Service to check stock availability"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{INVENTORY_SERVICE_URL}/inventory/{product_id}"
            )
            if response.status_code == 200:
                inventory = response.json()
                return inventory["available_quantity"] >= quantity
            return False
        except httpx.RequestError:
            # If inventory service is down, allow order (saga pattern would handle rollback)
            return True


async def reserve_inventory(product_id: int, quantity: int) -> bool:
    """Reserve inventory items"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{INVENTORY_SERVICE_URL}/inventory/reserve",
                json={"product_id": product_id, "quantity": quantity},
            )
            return response.status_code == 200
        except httpx.RequestError:
            return False


async def send_order_notification(user_id: int, order_id: int, status: str):
    """Send notification about order status"""
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                f"{NOTIFICATION_SERVICE_URL}/notifications/send",
                json={
                    "user_id": user_id,
                    "type": "order_update",
                    "message": f"Order #{order_id} is now {status}",
                    "data": {"order_id": order_id, "status": status},
                },
            )
        except httpx.RequestError:
            # Notification failure shouldn't block order creation
            pass


# ===== ROUTES =====
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "order-service"}


@app.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Create a new order"""

    if not order_data.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must contain at least one item",
        )

    # Calculate total amount and check inventory
    total_amount = 0.0
    order_items_data = []

    for item in order_data.items:
        # Get product price
        price = await get_product_price(item.product_id)

        # Check inventory
        has_stock = await check_inventory(item.product_id, item.quantity)
        if not has_stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {item.product_id} is out of stock",
            )

        item_total = price * item.quantity
        total_amount += item_total

        order_items_data.append(
            {"product_id": item.product_id, "quantity": item.quantity, "price": price}
        )

    # Create order
    db_order = Order(
        user_id=user_id, total_amount=total_amount, status=OrderStatus.PENDING.value
    )

    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Create order items
    for item_data in order_items_data:
        db_item = OrderItem(order_id=db_order.id, **item_data)
        db.add(db_item)

        # Reserve inventory
        await reserve_inventory(item_data["product_id"], item_data["quantity"])

    db.commit()
    db.refresh(db_order)

    # Send notification asynchronously
    asyncio.create_task(
        send_order_notification(user_id, db_order.id, OrderStatus.PENDING.value)
    )

    return OrderResponse.from_orm(db_order)


@app.get("/orders", response_model=List[OrderResponse])
async def list_orders(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
):
    """List all orders for current user"""
    orders = (
        db.query(Order)
        .filter(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [OrderResponse.from_orm(order) for order in orders]


@app.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get order details"""
    order = (
        db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).first()
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    return OrderResponse.from_orm(order)


@app.patch("/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    status: OrderStatus,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Update order status"""
    order = (
        db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).first()
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    order.status = status.value
    order.updated_at = datetime.utcnow()
    db.commit()

    # Send notification
    asyncio.create_task(send_order_notification(user_id, order_id, status.value))

    return {"message": "Order status updated", "status": status.value}


@app.post("/orders/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Cancel an order"""
    order = (
        db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).first()
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    if order.status in [OrderStatus.SHIPPED.value, OrderStatus.DELIVERED.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel order in current status",
        )

    order.status = OrderStatus.CANCELLED.value
    order.updated_at = datetime.utcnow()
    db.commit()

    # Release inventory (compensation in saga pattern)
    for item in order.items:
        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    f"{INVENTORY_SERVICE_URL}/inventory/release",
                    json={"product_id": item.product_id, "quantity": item.quantity},
                )
            except httpx.RequestError:
                pass

    return {"message": "Order cancelled successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8003)
