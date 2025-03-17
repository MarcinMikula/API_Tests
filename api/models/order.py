from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from api.database.db_config import Base
import datetime

# Importujemy klasy Customer i Product
from api.models.customer import Customer
from api.models.product import Product

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    quantity = Column(Integer)
    order_date = Column(DateTime, default=datetime.datetime.utcnow)
    total_price = Column(Float)

    # Relacje
    customer = relationship("Customer", back_populates="orders")
    product = relationship("Product", back_populates="orders")

# Aktualizacja modeli Customer i Product, aby uwzględnić relacje
Customer.orders = relationship("Order", order_by=Order.id, back_populates="customer")
Product.orders = relationship("Order", order_by=Order.id, back_populates="product")