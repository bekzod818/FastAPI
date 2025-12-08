from fastapi import FastAPI, HTTPException, Depends, Header, status
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import httpx
import asyncio
import os
import enum
import uuid

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://user:password@payment-db:5432/paymentdb"
)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Service URLs
ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://order-service:8003")
NOTIFICATION_SERVICE_URL = os.getenv(
    "NOTIFICATION_SERVICE_URL", "http://notification-service:8005"
)

app = FastAPI(
    title="Payment Service",
    description="Payment processing microservice",
    version="1.0.0",
)


# ===== ENUMS =====
class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, enum.Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"


# ===== DATABASE MODELS =====
class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    payment_method = Column(String, nullable=False)
    status = Column(String, default=PaymentStatus.PENDING.value)
    transaction_id = Column(String, unique=True, index=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Create tables
Base.metadata.create_all(bind=engine)


# ===== PYDANTIC SCHEMAS =====
class PaymentCreate(BaseModel):
    order_id: int
    amount: float
    payment_method: PaymentMethod
    currency: str = "USD"
    card_number: Optional[str] = None  # Last 4 digits only in production
    card_holder: Optional[str] = None


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    user_id: int
    amount: float
    currency: str
    payment_method: str
    status: str
    transaction_id: str
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RefundRequest(BaseModel):
    reason: Optional[str] = None


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
async def process_payment_gateway(
    amount: float, payment_method: str, card_details: dict = None
) -> tuple[bool, str, Optional[str]]:
    """
    Simulate payment gateway processing
    In production, integrate with Stripe, PayPal, etc.
    """
    # Simulate processing delay
    await asyncio.sleep(1)

    # Generate transaction ID
    transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"

    # Simulate 95% success rate
    import random

    success = random.random() < 0.95

    if success:
        return True, transaction_id, None
    else:
        return False, transaction_id, "Payment declined by bank"


async def update_order_payment_status(order_id: int, payment_id: int, status: str):
    """Update order with payment information"""
    async with httpx.AsyncClient() as client:
        try:
            await client.patch(
                f"{ORDER_SERVICE_URL}/orders/{order_id}/payment",
                json={"payment_id": payment_id, "status": status},
            )
        except httpx.RequestError:
            pass


async def send_payment_notification(
    user_id: int, payment_id: int, status: str, amount: float
):
    """Send notification about payment status"""
    async with httpx.AsyncClient() as client:
        try:
            message = f"Payment of ${amount:.2f} is {status}"
            await client.post(
                f"{NOTIFICATION_SERVICE_URL}/notifications/send",
                json={
                    "user_id": user_id,
                    "type": "payment_update",
                    "message": message,
                    "data": {
                        "payment_id": payment_id,
                        "status": status,
                        "amount": amount,
                    },
                },
            )
        except httpx.RequestError:
            pass


# ===== ROUTES =====
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "payment-service"}


@app.post(
    "/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED
)
async def create_payment(
    payment_data: PaymentCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Process a new payment"""

    # Check if payment already exists for this order
    existing_payment = (
        db.query(Payment)
        .filter(
            Payment.order_id == payment_data.order_id,
            Payment.status == PaymentStatus.COMPLETED.value,
        )
        .first()
    )

    if existing_payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment already completed for this order",
        )

    # Create payment record
    db_payment = Payment(
        order_id=payment_data.order_id,
        user_id=user_id,
        amount=payment_data.amount,
        currency=payment_data.currency,
        payment_method=payment_data.payment_method.value,
        status=PaymentStatus.PROCESSING.value,
        transaction_id=f"PENDING-{uuid.uuid4().hex[:8]}",
    )

    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)

    # Process payment through gateway
    card_details = (
        {
            "card_number": payment_data.card_number,
            "card_holder": payment_data.card_holder,
        }
        if payment_data.card_number
        else None
    )

    success, transaction_id, error_msg = await process_payment_gateway(
        payment_data.amount, payment_data.payment_method.value, card_details
    )

    # Update payment record
    if success:
        db_payment.status = PaymentStatus.COMPLETED.value
        db_payment.transaction_id = transaction_id

        # Update order status
        asyncio.create_task(
            update_order_payment_status(
                payment_data.order_id, db_payment.id, "confirmed"
            )
        )
    else:
        db_payment.status = PaymentStatus.FAILED.value
        db_payment.transaction_id = transaction_id
        db_payment.error_message = error_msg

    db_payment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_payment)

    # Send notification
    asyncio.create_task(
        send_payment_notification(
            user_id, db_payment.id, db_payment.status, db_payment.amount
        )
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=error_msg or "Payment processing failed",
        )

    return PaymentResponse.from_orm(db_payment)


@app.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get payment details"""
    payment = (
        db.query(Payment)
        .filter(Payment.id == payment_id, Payment.user_id == user_id)
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found"
        )

    return PaymentResponse.from_orm(payment)


@app.get("/payments/order/{order_id}", response_model=PaymentResponse)
async def get_payment_by_order(
    order_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get payment for an order"""
    payment = (
        db.query(Payment)
        .filter(Payment.order_id == order_id, Payment.user_id == user_id)
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found for this order",
        )

    return PaymentResponse.from_orm(payment)


@app.post("/payments/{payment_id}/refund", response_model=PaymentResponse)
async def refund_payment(
    payment_id: int,
    refund_data: RefundRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Process a refund"""
    payment = (
        db.query(Payment)
        .filter(Payment.id == payment_id, Payment.user_id == user_id)
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found"
        )

    if payment.status != PaymentStatus.COMPLETED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only completed payments can be refunded",
        )

    # Process refund through gateway
    # In production, call payment gateway's refund API
    await asyncio.sleep(1)  # Simulate processing

    payment.status = PaymentStatus.REFUNDED.value
    payment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(payment)

    # Send notification
    asyncio.create_task(
        send_payment_notification(user_id, payment_id, "refunded", payment.amount)
    )

    return PaymentResponse.from_orm(payment)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8004)
