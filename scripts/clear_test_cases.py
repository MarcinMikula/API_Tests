from sqlalchemy.orm import Session
from api.database.db_config import SessionLocal
from api.models.test_case import TestCase

def clear_test_cases():
    db: Session = SessionLocal()
    try:
        db.query(TestCase).delete()
        db.commit()
        print("Usunięto wszystkie przypadki testowe z tabeli test_cases.")
    except Exception as e:
        print(f"Błąd podczas usuwania: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_test_cases()