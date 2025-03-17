from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from api.database.db_config import Base
import datetime

class TestResult(Base):
    __tablename__ = "test_results"
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(String, ForeignKey("test_cases.test_id"), index=True)  # Powiązanie z test_cases
    result = Column(String)  # "passed" lub "not passed"
    actual_status = Column(Integer)
    actual_response = Column(String)
    defect_key = Column(String, nullable=True)  # Klucz defektu w JIRA, np. "SCRUM-77"
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    duration_ms = Column(Integer, nullable=True)  # Czas trwania testu w milisekundach
    environment = Column(String, default="local")  # Środowisko testowe
    tester = Column(String, default="automated")  # Osoba/urządzenie wykonujące test
    retry_count = Column(Integer, default=0)  # Liczba prób wykonania testu

    test_case = relationship("TestCase", back_populates="results")