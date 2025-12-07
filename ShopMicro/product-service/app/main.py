from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Float,
    Boolean,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import os

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://user:password@product-db:5432/productdb"
)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI(
    title="Product Service", description="Product catalog microservice", version="1.0.0"
)


# ===== DATABASE MODELS =====
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    category = Column(String, index=True)
    sku = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Create tables
Base.metadata.create_all(bind=engine)


# ===== PYDANTIC SCHEMAS =====
class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: str
    sku: str
    image_url: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None
    image_url: Optional[str] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    category: str
    sku: str
    is_active: bool
    image_url: Optional[str]
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


# ===== ROUTES =====
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "product-service"}


@app.post(
    "/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED
)
async def create_product(product_data: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product"""

    # Check if SKU already exists
    existing_product = db.query(Product).filter(Product.sku == product_data.sku).first()
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this SKU already exists",
        )

    # Create product
    db_product = Product(**product_data.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return ProductResponse.from_orm(db_product)


@app.get("/products", response_model=List[ProductResponse])
async def list_products(
    skip: int = 0,
    limit: int = 50,
    category: Optional[str] = None,
    search: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    """List all products with filtering"""
    query = db.query(Product)

    if active_only:
        query = query.filter(Product.is_active == True)

    if category:
        query = query.filter(Product.category == category)

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    products = query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()

    return [ProductResponse.from_orm(p) for p in products]


@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get product by ID"""
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    return ProductResponse.from_orm(product)


@app.get("/products/sku/{sku}", response_model=ProductResponse)
async def get_product_by_sku(sku: str, db: Session = Depends(get_db)):
    """Get product by SKU"""
    product = db.query(Product).filter(Product.sku == sku).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    return ProductResponse.from_orm(product)


@app.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int, product_data: ProductUpdate, db: Session = Depends(get_db)
):
    """Update product"""
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    # Update fields
    update_data = product_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    product.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(product)

    return ProductResponse.from_orm(product)


@app.delete("/products/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Soft delete product (mark as inactive)"""
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    product.is_active = False
    product.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Product deleted successfully"}


@app.get("/products/category/{category}", response_model=List[ProductResponse])
async def get_products_by_category(
    category: str, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)
):
    """Get all products in a category"""
    products = (
        db.query(Product)
        .filter(Product.category == category, Product.is_active == True)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [ProductResponse.from_orm(p) for p in products]


@app.get("/categories")
async def list_categories(db: Session = Depends(get_db)):
    """Get list of all product categories"""
    categories = db.query(Product.category).distinct().all()
    return {"categories": [cat[0] for cat in categories if cat[0]]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
