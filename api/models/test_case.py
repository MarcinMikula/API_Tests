from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from api.database.db_config import Base

class TestCase(Base):
    __tablename__ = "test_cases"
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(String, unique=True, index=True)
    description = Column(String)
    endpoint = Column(String)
    method = Column(String)
    test_type = Column(String)
    expected_status = Column(Integer)
    expected_response = Column(String)

    results = relationship("TestResult", order_by="TestResult.id", back_populates="test_case")