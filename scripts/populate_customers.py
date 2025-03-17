from sqlalchemy.orm import Session
from api.database.db_config import SessionLocal
from api.database.db_utils import init_db
from api.models.customer import Customer

def populate_customers():
    # Inicjalizujemy bazę danych (tworzymy tabele, jeśli nie istnieją)
    init_db()
    print("Tabele w bazie danych zostały zainicjowane.")

    # Otwieramy sesję bazy danych
    db: Session = SessionLocal()
    try:
        # Lista klientów do dodania
        customers = [
            Customer(first_name="Jan", last_name="Kowalski", email="jan.kowalski@example.com", phone="123456789", address="ul. Kwiatowa 1, Warszawa"),
            Customer(first_name="Anna", last_name="Nowak", email="anna.nowak@example.com", phone="987654321", address="ul. Słoneczna 2, Kraków"),
            Customer(first_name="Piotr", last_name="Wiśniewski", email="piotr.wisniewski@example.com", phone=None, address="ul. Leśna 3, Gdańsk"),
            Customer(first_name="Katarzyna", last_name="Zielińska", email="katarzyna.zielinska@example.com", phone="456123789", address="ul. Polna 4, Wrocław"),
            Customer(first_name="Tomasz", last_name="Lewandowski", email="tomasz.lewandowski@example.com", phone="789123456", address="ul. Morska 5, Gdynia"),
        ]

        # Dodajemy klientów do bazy
        for customer in customers:
            db.add(customer)
            print(f"Dodano klienta: {customer.first_name} {customer.last_name}")

        # Zatwierdzamy zmiany
        db.commit()
        print("Dodano 5 klientów do tabeli customers!")
    except Exception as e:
        print(f"Wystąpił błąd podczas dodawania klientów: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_customers()