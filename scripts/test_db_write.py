from sqlalchemy.orm import Session
from api.database.db_config import SessionLocal
from api.models.test_result import TestResult


def test_db_write():
    db: Session = SessionLocal()
    try:
        print("Sesja bazy danych otwarta")
        # Tworzymy testowy rekord
        test_result = TestResult(
            test_id="TEST_020",
            result="passed",
            actual_status=200,
            actual_response="Test response",
            defect_key=None,
            duration_ms=100,
            environment="local",
            tester="automated",
            retry_count=0
        )
        db.add(test_result)
        db.commit()
        print("Zapis testowego rekordu zakończony sukcesem")

        # Sprawdzamy, czy rekord został zapisany
        saved_result = db.query(TestResult).filter(TestResult.test_id == "TEST_001").first()
        if saved_result:
            print(
                f"Rekord zapisany: {saved_result.test_id}, result={saved_result.result}, timestamp={saved_result.timestamp}")
        else:
            print("UWAGA: Rekord NIE został zapisany!")
    except Exception as e:
        print(f"Błąd podczas zapisu do bazy danych: {e}")
        db.rollback()
    finally:
        db.close()
        print("Sesja bazy danych zamknięta")


if __name__ == "__main__":
    test_db_write()