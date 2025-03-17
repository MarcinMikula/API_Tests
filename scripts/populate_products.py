from sqlalchemy.orm import Session
from api.database.db_config import SessionLocal
from api.database.db_utils import init_db
from api.models.product import Product

def populate_products():
    # Inicjalizujemy bazę danych (tworzymy tabele, jeśli nie istnieją)
    init_db()
    print("Tabele w bazie danych zostały zainicjowane.")

    # Otwieramy sesję bazy danych
    db: Session = SessionLocal()
    try:
        # Lista produktów do dodania
        products = [
            Product(name="Laptop", description="Laptop gamingowy", price=4500.99, available=True, stock=10),
            Product(name="Smartfon", description="Smartfon z 5G", price=2500.50, available=True, stock=25),
            Product(name="Słuchawki", description="Bezprzewodowe słuchawki", price=299.99, available=True, stock=50),
            Product(name="Klawiatura", description="Klawiatura mechaniczna", price=399.00, available=False, stock=0),
            Product(name="Myszka", description="Myszka optyczna", price=129.99, available=True, stock=100),
            Product(name="Monitor", description="Monitor 4K 27 cali", price=1800.00, available=True, stock=15),
            Product(name="Dysk SSD", description="Dysk SSD 1TB", price=550.00, available=True, stock=30),
            Product(name="Kamera internetowa", description="Kamera HD", price=199.99, available=False, stock=5),
            Product(name="Router", description="Router Wi-Fi 6", price=399.50, available=True, stock=20),
            Product(name="Drukarka", description="Drukarka laserowa", price=799.00, available=True, stock=8),
            Product(name="Tablet", description="Tablet 10 cali", price=1200.00, available=True, stock=12),
            Product(name="Głośniki", description="Głośniki Bluetooth", price=249.99, available=True, stock=40),
            Product(name="Projektor", description="Projektor Full HD", price=2200.00, available=False, stock=3),
            Product(name="Skaner", description="Skaner biurowy", price=450.00, available=True, stock=7),
            Product(name="Etui na laptopa", description="Etui 15 cali", price=89.99, available=True, stock=60),
            Product(name="Podstawka chłodząca", description="Podstawka pod laptop", price=149.99, available=True, stock=25),
            Product(name="Kabel HDMI", description="Kabel HDMI 2m", price=39.99, available=True, stock=200),
            Product(name="Pendrive", description="Pendrive 64GB", price=59.99, available=True, stock=150),
            Product(name="Zasilacz", description="Zasilacz uniwersalny", price=99.99, available=False, stock=0),
            Product(name="Smartwatch", description="Smartwatch sportowy", price=699.99, available=True, stock=18),
        ]

        # Dodajemy produkty do bazy
        for product in products:
            db.add(product)
            print(f"Dodano produkt: {product.name}")

        # Zatwierdzamy zmiany
        db.commit()
        print("Dodano 20 produktów do tabeli products!")
    except Exception as e:
        print(f"Wystąpił błąd podczas dodawania produktów: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_products()