import bcrypt
import settings
from db_initializer import Base

import jwt
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    LargeBinary,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
)


class User(Base):
    """Models a user table"""

    __tablename__ = "users"
    id = Column(Integer, nullable=False, primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(LargeBinary, nullable=False)
    is_active = Column(Boolean, default=False)

    UniqueConstraint("email", name="uq_user_email")
    PrimaryKeyConstraint("id", name="pk_user_id")

    def __repr__(self):
        """Returns string representation of model instance"""
        return f"<User {self.full_name!r}>"

    @staticmethod
    def hash_password(password):
        """Transforms password from it's raw textual form to cryptographic hashes"""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    def validate_password(self, password):
        """Confirms password validity"""
        return bcrypt.checkpw(password.encode(), self.hashed_password)

    def generate_token(self) -> dict:
        """Generate access token for user"""
        return {
            "access_token": jwt.encode(
                {"full_name": self.full_name, "email": self.email}, settings.SECRET_KEY
            )
        }
