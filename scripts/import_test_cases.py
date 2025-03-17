import os
import pandas as pd
from sqlalchemy.orm import Session
from api.database.db_config import SessionLocal, DATABASE_URL
from api.database.db_utils import init_db
from api.models.test_case import TestCase

# Dynamiczne określenie ścieżki do pliku CSV
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE_PATH = os.path.join(BASE_DIR, "tests", "test_data", "test_cases.csv")

def import_test_cases():
    # Wyświetlamy ścieżkę do bazy danych
    print(f"Ścieżka do bazy danych: {DATABASE_URL}")

    # Inicjalizujemy bazę danych (tworzymy tabele, jeśli nie istnieją)
    init_db()
    print("Tabele w bazie danych zostały zainicjowane.")

    # Otwieramy sesję bazy danych
    db: Session = SessionLocal()
    try:
        # Wczytujemy plik CSV linia po linii, aby debugować
        print(f"Próbuję wczytać plik CSV: {CSV_FILE_PATH}")
        with open(CSV_FILE_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                print(f"Linia {i + 1}: {line.strip()}")
                fields = line.strip().split(',')
                print(f"Liczba pól w linii {i + 1}: {len(fields)}")

        # Wczytujemy plik CSV za pomocą pandas
        df = pd.read_csv(CSV_FILE_PATH)
        print(f"Wczytano {len(df)} przypadków testowych z pliku CSV.")
        print("Wczytane dane z CSV:")
        print(df)

        # Iterujemy po wierszach w pliku CSV
        for index, row in df.iterrows():
            print(f"Przetwarzam wiersz {index + 1}: {row.to_dict()}")

            existing_test = db.query(TestCase).filter(TestCase.test_id == row['test_id']).first()
            if existing_test:
                print(f"Przypadek testowy {row['test_id']} już istnieje, pomijam.")
                continue

            test_case = TestCase(
                test_id=row['test_id'],
                description=row['description'],
                endpoint=row['endpoint'],
                method=row['method'],
                test_type=row['test_type'],
                expected_status=row['expected_status'],
                expected_response=row['expected_response']
            )
            db.add(test_case)
            print(f"Dodano przypadek testowy: {row['test_id']}")

        db.commit()
        print("Import zakończony sukcesem!")

        saved_cases = db.query(TestCase).all()
        print(f"Liczba zapisanych przypadków testowych w bazie: {len(saved_cases)}")
        for case in saved_cases:
            print(f"Zapisany przypadek: {case.test_id}, {case.description}")

    except Exception as e:
        print(f"Wystąpił błąd podczas importu: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import_test_cases()