from fastapi import FastAPI, HTTPException, BackgroundTasks, status
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List, Dict, Any
import httpx
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://user:password@notification-db:5432/notificationdb"
)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Email configuration (use environment variables in production)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@shopmicro.com")

# Service URLs
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8001")

app = FastAPI(
    title="Notification Service",
    description="Notification and messaging microservice",
    version="1.0.0",
)


# ===== DATABASE MODELS =====
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    type = Column(String, nullable=False)  # order_update, payment_update, etc.
    channel = Column(String, default="in_app")  # in_app, email, sms
    subject = Column(String, nullable=True)
    message = Column(Text, nullable=False)
    data = Column(Text, nullable=True)  # JSON string for additional data
    is_read = Column(Boolean, default=False)
    sent = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Create tables
Base.metadata.create_all(bind=engine)


# ===== PYDANTIC SCHEMAS =====
class NotificationCreate(BaseModel):
    user_id: int
    type: str
    message: str
    subject: Optional[str] = None
    channel: str = "in_app"
    data: Optional[Dict[str, Any]] = None


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    type: str
    channel: str
    subject: Optional[str]
    message: str
    data: Optional[str]
    is_read: bool
    sent: bool
    sent_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class EmailNotification(BaseModel):
    to_email: EmailStr
    subject: str
    body: str
    is_html: bool = False


# ===== UTILITY FUNCTIONS =====
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_user_email(user_id: int) -> Optional[str]:
    """Fetch user email from User Service"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{USER_SERVICE_URL}/users/{user_id}")
            if response.status_code == 200:
                user_data = response.json()
                return user_data.get("email")
        except httpx.RequestError:
            pass
    return None


def send_email_smtp(to_email: str, subject: str, body: str, is_html: bool = False):
    """Send email using SMTP"""
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print(f"[SIMULATED EMAIL] To: {to_email}, Subject: {subject}")
        print(f"Body: {body}")
        return

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = FROM_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject

        mime_type = "html" if is_html else "plain"
        msg.attach(MIMEText(body, mime_type))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)

        print(f"Email sent successfully to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")


async def process_notification(notification_id: int, db: Session):
    """Process and send notification based on channel"""
    notification = (
        db.query(Notification).filter(Notification.id == notification_id).first()
    )

    if not notification or notification.sent:
        return

    if notification.channel == "email":
        # Get user email
        user_email = await get_user_email(notification.user_id)
        if user_email:
            send_email_smtp(
                to_email=user_email,
                subject=notification.subject or "Notification from ShopMicro",
                body=notification.message,
                is_html=False,
            )
    elif notification.channel == "sms":
        # Simulate SMS sending
        print(f"[SIMULATED SMS] To User {notification.user_id}: {notification.message}")

    # Mark as sent
    notification.sent = True
    notification.sent_at = datetime.utcnow()
    db.commit()


# ===== ROUTES =====
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "notification-service"}


@app.post(
    "/notifications/send",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def send_notification(
    notification_data: NotificationCreate,
    background_tasks: BackgroundTasks,
    db: Session = next(get_db()),
):
    """Create and send a notification"""

    # Convert data dict to JSON string
    data_json = json.dumps(notification_data.data) if notification_data.data else None

    # Create notification record
    db_notification = Notification(
        user_id=notification_data.user_id,
        type=notification_data.type,
        channel=notification_data.channel,
        subject=notification_data.subject,
        message=notification_data.message,
        data=data_json,
    )

    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)

    # Process notification in background
    background_tasks.add_task(process_notification, db_notification.id, db)

    return NotificationResponse.from_orm(db_notification)


@app.get("/notifications/user/{user_id}", response_model=List[NotificationResponse])
async def get_user_notifications(
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    unread_only: bool = False,
    db: Session = next(get_db()),
):
    """Get all notifications for a user"""
    query = db.query(Notification).filter(Notification.user_id == user_id)

    if unread_only:
        query = query.filter(Notification.is_read == False)

    notifications = (
        query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    )

    return [NotificationResponse.from_orm(n) for n in notifications]


@app.patch("/notifications/{notification_id}/read")
async def mark_as_read(notification_id: int, db: Session = next(get_db())):
    """Mark notification as read"""
    notification = (
        db.query(Notification).filter(Notification.id == notification_id).first()
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found"
        )

    notification.is_read = True
    db.commit()

    return {"message": "Notification marked as read"}


@app.post("/notifications/email", status_code=status.HTTP_202_ACCEPTED)
async def send_email(email_data: EmailNotification, background_tasks: BackgroundTasks):
    """Send a direct email notification"""
    background_tasks.add_task(
        send_email_smtp,
        email_data.to_email,
        email_data.subject,
        email_data.body,
        email_data.is_html,
    )

    return {"message": "Email queued for sending"}


@app.delete("/notifications/{notification_id}")
async def delete_notification(notification_id: int, db: Session = next(get_db())):
    """Delete a notification"""
    notification = (
        db.query(Notification).filter(Notification.id == notification_id).first()
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found"
        )

    db.delete(notification)
    db.commit()

    return {"message": "Notification deleted"}


@app.get("/notifications/stats/{user_id}")
async def get_notification_stats(user_id: int, db: Session = next(get_db())):
    """Get notification statistics for a user"""
    total = db.query(Notification).filter(Notification.user_id == user_id).count()
    unread = (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.is_read == False)
        .count()
    )

    return {
        "user_id": user_id,
        "total_notifications": total,
        "unread_notifications": unread,
        "read_notifications": total - unread,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8005)
