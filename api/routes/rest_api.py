from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database.db_config import SessionLocal
from api.models.product import Product
from api.models.test_case import TestCase
from api.models.customer import Customer
from api.models.order import Order
from pydantic import BaseModel, Field

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Model Pydantic do walidacji danych wejściowych dla produktu
class ProductCreate(BaseModel):
    name: str = Field(..., max_length=100)  # Pole wymagane
    description: str = Field(...)  # Pole wymagane
    price: float = Field(..., gt=0)  # Pole wymagane
    available: bool = Field(default=True)
    stock: int = Field(default=0, ge=0)

class ProductUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    description: str | None = None
    price: float | None = Field(None, gt=0)
    available: bool | None = None
    stock: int | None = Field(None, ge=0)

# CRUD dla Products
@router.get("/products")
async def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@router.get("/products/{product_id}")
async def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/products", status_code=201)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.put("/products/{product_id}")
async def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in product.dict(exclude_unset=True).items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/products/{product_id}", status_code=204)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return {"detail": "Product deleted"}

# Pozostałe endpointy
@router.get("/customers")
async def get_customers(db: Session = Depends(get_db)):
    return db.query(Customer).all()

@router.get("/orders")
async def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()

@router.get("/test-cases")
async def get_test_cases(db: Session = Depends(get_db)):
    return db.query(TestCase).all()