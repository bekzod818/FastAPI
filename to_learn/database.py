from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine

engine = create_engine("postgresql://postgres:postgres@localhost/fast", echo=True)

Base = declarative_base()

SessionLocal = sessionmaker(bind=engine)