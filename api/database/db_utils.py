from .db_config import Base, engine
# Importujemy wszystkie modele, aby SQLAlchemy je rozpoznał
from api.models.product import Product
from api.models.customer import Customer
from api.models.order import Order
from api.models.test_case import TestCase
from api.models.test_result import TestResult  # Upewniamy się, że jest zaimportowany

def init_db():
    Base.metadata.create_all(bind=engine)