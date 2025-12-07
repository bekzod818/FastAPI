from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy import create_engine, Column, Integer, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import os

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://user:password@inventory-db:5432/inventorydb"
)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI(
    title="Inventory Service",
    description="Inventory management microservice",
    version="1.0.0",
)


# ===== DATABASE MODELS =====
class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, unique=True, nullable=False, index=True)
    available_quantity = Column(Integer, nullable=False, default=0)
    reserved_quantity = Column(Integer, nullable=False, default=0)
    reorder_level = Column(Integer, default=10)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False, index=True)
    transaction_type = Column(String, nullable=False)  # restock, reserve, release, sold
    quantity = Column(Integer, nullable=False)
    reference_id = Column(Integer, nullable=True)  # order_id or other reference
    created_at = Column(DateTime, default=datetime.utcnow)


# Create tables
Base.metadata.create_all(bind=engine)


# ===== PYDANTIC SCHEMAS =====
class InventoryCreate(BaseModel):
    product_id: int
    available_quantity: int
    reorder_level: int = 10


class InventoryUpdate(BaseModel):
    available_quantity: Optional[int] = None
    reorder_level: Optional[int] = None


class InventoryResponse(BaseModel):
    id: int
    product_id: int
    available_quantity: int
    reserved_quantity: int
    reorder_level: int
    total_quantity: int
    needs_reorder: bool
    updated_at: datetime

    class Config:
        from_attributes = True


class ReserveRequest(BaseModel):
    product_id: int
    quantity: int
    order_id: Optional[int] = None


class RestockRequest(BaseModel):
    product_id: int
    quantity: int


class TransactionResponse(BaseModel):
    id: int
    product_id: int
    transaction_type: str
    quantity: int
    reference_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# ===== DEPENDENCIES =====
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ===== UTILITY FUNCTIONS =====
def create_transaction(
    db: Session,
    product_id: int,
    transaction_type: str,
    quantity: int,
    reference_id: Optional[int] = None,
):
    """Create an inventory transaction record"""
    transaction = InventoryTransaction(
        product_id=product_id,
        transaction_type=transaction_type,
        quantity=quantity,
        reference_id=reference_id,
    )
    db.add(transaction)
    db.commit()


# ===== ROUTES =====
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "inventory-service"}


@app.post(
    "/inventory", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED
)
async def create_inventory(
    inventory_data: InventoryCreate, db: Session = Depends(get_db)
):
    """Create inventory record for a product"""

    # Check if inventory already exists
    existing = (
        db.query(Inventory)
        .filter(Inventory.product_id == inventory_data.product_id)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inventory already exists for this product",
        )

    # Create inventory
    db_inventory = Inventory(**inventory_data.dict())
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)

    # Create transaction
    create_transaction(
        db,
        inventory_data.product_id,
        "initial_stock",
        inventory_data.available_quantity,
    )

    # Calculate derived fields
    response = InventoryResponse.from_orm(db_inventory)
    response.total_quantity = (
        db_inventory.available_quantity + db_inventory.reserved_quantity
    )
    response.needs_reorder = (
        db_inventory.available_quantity <= db_inventory.reorder_level
    )

    return response


@app.get("/inventory/{product_id}", response_model=InventoryResponse)
async def get_inventory(product_id: int, db: Session = Depends(get_db)):
    """Get inventory for a product"""
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()

    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory not found for this product",
        )

    # Calculate derived fields
    response = InventoryResponse.from_orm(inventory)
    response.total_quantity = inventory.available_quantity + inventory.reserved_quantity
    response.needs_reorder = inventory.available_quantity <= inventory.reorder_level

    return response


@app.post("/inventory/reserve", status_code=status.HTTP_200_OK)
async def reserve_inventory(
    reserve_data: ReserveRequest, db: Session = Depends(get_db)
):
    """Reserve inventory for an order"""
    inventory = (
        db.query(Inventory)
        .filter(Inventory.product_id == reserve_data.product_id)
        .first()
    )

    if not inventory:
        # Auto-create inventory if it doesn't exist
        inventory = Inventory(
            product_id=reserve_data.product_id,
            available_quantity=0,
            reserved_quantity=0,
        )
        db.add(inventory)
        db.commit()
        db.refresh(inventory)

    # Check availability
    if inventory.available_quantity < reserve_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient inventory. Available: {inventory.available_quantity}",
        )

    # Reserve inventory
    inventory.available_quantity -= reserve_data.quantity
    inventory.reserved_quantity += reserve_data.quantity
    inventory.updated_at = datetime.utcnow()
    db.commit()

    # Create transaction
    create_transaction(
        db,
        reserve_data.product_id,
        "reserve",
        reserve_data.quantity,
        reserve_data.order_id,
    )

    return {
        "message": "Inventory reserved successfully",
        "product_id": reserve_data.product_id,
        "quantity_reserved": reserve_data.quantity,
        "available_quantity": inventory.available_quantity,
    }


@app.post("/inventory/release")
async def release_inventory(
    reserve_data: ReserveRequest, db: Session = Depends(get_db)
):
    """Release reserved inventory (e.g., order cancelled)"""
    inventory = (
        db.query(Inventory)
        .filter(Inventory.product_id == reserve_data.product_id)
        .first()
    )

    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Inventory not found"
        )

    # Release inventory
    if inventory.reserved_quantity < reserve_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot release more than reserved quantity",
        )

    inventory.reserved_quantity -= reserve_data.quantity
    inventory.available_quantity += reserve_data.quantity
    inventory.updated_at = datetime.utcnow()
    db.commit()

    # Create transaction
    create_transaction(
        db,
        reserve_data.product_id,
        "release",
        reserve_data.quantity,
        reserve_data.order_id,
    )

    return {"message": "Inventory released successfully"}


@app.post("/inventory/sold")
async def mark_as_sold(reserve_data: ReserveRequest, db: Session = Depends(get_db)):
    """Mark reserved inventory as sold"""
    inventory = (
        db.query(Inventory)
        .filter(Inventory.product_id == reserve_data.product_id)
        .first()
    )

    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Inventory not found"
        )

    # Mark as sold
    if inventory.reserved_quantity < reserve_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot sell more than reserved quantity",
        )

    inventory.reserved_quantity -= reserve_data.quantity
    inventory.updated_at = datetime.utcnow()
    db.commit()

    # Create transaction
    create_transaction(
        db,
        reserve_data.product_id,
        "sold",
        reserve_data.quantity,
        reserve_data.order_id,
    )

    return {"message": "Inventory marked as sold"}


@app.post("/inventory/restock")
async def restock_inventory(
    restock_data: RestockRequest, db: Session = Depends(get_db)
):
    """Add stock to inventory"""
    inventory = (
        db.query(Inventory)
        .filter(Inventory.product_id == restock_data.product_id)
        .first()
    )

    if not inventory:
        # Create new inventory if doesn't exist
        inventory = Inventory(
            product_id=restock_data.product_id,
            available_quantity=restock_data.quantity,
            reserved_quantity=0,
        )
        db.add(inventory)
    else:
        inventory.available_quantity += restock_data.quantity
        inventory.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(inventory)

    # Create transaction
    create_transaction(db, restock_data.product_id, "restock", restock_data.quantity)

    return {
        "message": "Inventory restocked successfully",
        "product_id": restock_data.product_id,
        "quantity_added": restock_data.quantity,
        "new_quantity": inventory.available_quantity,
    }


@app.get("/inventory/low-stock", response_model=List[InventoryResponse])
async def get_low_stock_items(db: Session = Depends(get_db)):
    """Get items that need reordering"""
    inventories = (
        db.query(Inventory)
        .filter(Inventory.available_quantity <= Inventory.reorder_level)
        .all()
    )

    results = []
    for inv in inventories:
        response = InventoryResponse.from_orm(inv)
        response.total_quantity = inv.available_quantity + inv.reserved_quantity
        response.needs_reorder = True
        results.append(response)

    return results


@app.get(
    "/inventory/transactions/{product_id}", response_model=List[TransactionResponse]
)
async def get_inventory_transactions(
    product_id: int, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)
):
    """Get transaction history for a product"""
    transactions = (
        db.query(InventoryTransaction)
        .filter(InventoryTransaction.product_id == product_id)
        .order_by(InventoryTransaction.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [TransactionResponse.from_orm(t) for t in transactions]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8006)
