from sqlalchemy import Column, Integer, String, Float, Boolean
from api.database.db_config import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    available = Column(Boolean, default=True)  # Domyślnie produkt jest dostępny
    stock = Column(Integer, default=0)         # Domyślnie brak na stanie