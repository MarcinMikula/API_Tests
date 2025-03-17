from sqlalchemy.orm import Session
from api.database.db_config import SessionLocal
from api.database.db_utils import init_db
from api.models.order import Order
import datetime

def populate_orders():
    # Inicjalizujemy bazę danych (tworzymy tabele, jeśli nie istnieją)
    init_db()
    print("Tabele w bazie danych zostały zainicjowane.")

    # Otwieramy sesję bazy danych
    db: Session = SessionLocal()
    try:
        # Lista zamówień do dodania
        orders = [
            Order(customer_id=1, product_id=1, quantity=2, total_price=9019.98, order_date=datetime.datetime(2025, 1, 15)),
            Order(customer_id=1, product_id=3, quantity=1, total_price=299.99, order_date=datetime.datetime(2025, 1, 16)),
            Order(customer_id=2, product_id=2, quantity=1, total_price=2500.50, order_date=datetime.datetime(2025, 2, 1)),
            Order(customer_id=2, product_id=5, quantity=3, total_price=389.97, order_date=datetime.datetime(2025, 2, 2)),
            Order(customer_id=3, product_id=6, quantity=1, total_price=1800.00, order_date=datetime.datetime(2025, 2, 10)),
            Order(customer_id=3, product_id=7, quantity=2, total_price=1100.00, order_date=datetime.datetime(2025, 2, 11)),
            Order(customer_id=4, product_id=9, quantity=1, total_price=399.50, order_date=datetime.datetime(2025, 3, 1)),
            Order(customer_id=4, product_id=11, quantity=1, total_price=1200.00, order_date=datetime.datetime(2025, 3, 2)),
            Order(customer_id=5, product_id=12, quantity=2, total_price=499.98, order_date=datetime.datetime(2025, 3, 5)),
            Order(customer_id=5, product_id=20, quantity=1, total_price=699.99, order_date=datetime.datetime(2025, 3, 6)),
        ]

        # Dodajemy zamówienia do bazy
        for order in orders:
            db.add(order)
            print(f"Dodano zamówienie: ID {order.id}, Klient ID {order.customer_id}, Produkt ID {order.product_id}")

        # Zatwierdzamy zmiany
        db.commit()
        print("Dodano 10 zamówień do tabeli orders!")
    except Exception as e:
        print(f"Wystąpił błąd podczas dodawania zamówień: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_orders()