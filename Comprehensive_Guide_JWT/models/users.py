from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    LargeBinary,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
)

from ..db_initializer import Base


class User(Base):
    """Models a user table"""

    __tablename__ = "users"
    id = Column(Integer, nullable=False, primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    hashed_password = Column(LargeBinary, nullable=False)
    is_active = Column(Boolean, default=False)

    UniqueConstraint("email", name="uq_user_email")
    PrimaryKeyConstraint("id", name="pk_user_id")

    def __repr__(self):
        """Returns string representation of model instance"""
        return f"<User {self.full_name!r}>"
