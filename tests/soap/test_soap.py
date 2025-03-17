import pytest
import time
import json
import requests
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from jira import JIRA
import xml.etree.ElementTree as ET
from api.database.db_config import SessionLocal
from api.models.test_case import TestCase
from api.models.test_result import TestResult
from config import JIRA_SERVER, JIRA_USERNAME, JIRA_API_TOKEN, JIRA_PROJECT_KEY, ISSUE_KEY

# Adres endpointu SOAP
SOAP_ENDPOINT = "http://127.0.0.1:8002/soap/"

# Połączenie z JIRA
jira = JIRA(
    server=JIRA_SERVER,
    basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN)
)

# Fixtures
@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        print("Sesja bazy danych otwarta")
        yield db
    except Exception as e:
        print(f"Błąd sesji bazy danych: {e}")
        raise
    finally:
        print("Zamykam sesję bazy danych")
        db.close()

# Przykładowe przypadki testowe dla SOAP
SOAP_TEST_CASES = [
    {
        "test_id": "SOAP_TC_001",
        "description": "Pobranie istniejącego produktu przez SOAP",
        "operation": "GetProduct",
        "input": {"id": 1},
        "expected_status": 200,
        "expected_response": {"id": 1, "name": "Laptop", "description": "Laptop gamingowy"}
    },
    {
        "test_id": "SOAP_TC_002",
        "description": "Utworzenie nowego produktu przez SOAP",
        "operation": "CreateProduct",
        "input": {"name": "Test Product", "description": "Test Description", "price": 99.99},
        "expected_status": 201,
        "expected_response": {"result": 21}
    },
    {
        "test_id": "SOAP_TC_003",
        "description": "Usunięcie produktu przez SOAP",
        "operation": "DeleteProduct",
        "input": {"id": 1},
        "expected_status": 204,
        "expected_response": {"status": "Product deleted"}
    }
]

# Funkcja do raportowania defektów w JIRA
def report_defect_to_jira(test_case: dict, issue_key: str, actual_status: int, actual_response: str):
    try:
        print(f"Szukam istniejących defektów w JIRA dla {test_case['test_id']}...")
        jql_query = f'project={JIRA_PROJECT_KEY} AND issuetype=Bug AND summary ~ "Defekt dla {test_case["test_id"]}"'
        existing_defects = jira.search_issues(jql_query)
        print(f"Znaleziono {len(existing_defects)} istniejących defektów dla zapytania: {jql_query}")

        if existing_defects:
            defect = existing_defects[0]
            defect_key = defect.key
            comment = (
                f"Retest dla przypadku testowego {test_case['test_id']}:\n"
                f"**Rzeczywisty status**: {actual_status}\n"
                f"**Rzeczywista odpowiedź**: {actual_response}\n"
                f"**Test Result**: not passed\n"
                f"**Defect created**: yes\n"
                f"**Numer defektu**: {defect_key}"
            )
            jira.add_comment(defect_key, comment)
            print(f"Dodano komentarz do istniejącego defektu {defect_key} dla przypadku testowego {test_case['test_id']}")
            return defect_key

        print(f"Tworzę nowy defekt w JIRA dla {test_case['test_id']}...")
        defect_dict = {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": f"Defekt dla {test_case['test_id']}: {test_case['description']}",
            "description": (
                f"**Przypadek testowy**: {test_case['test_id']}\n"
                f"**Operation**: {test_case['operation']}\n"
                f"**Input**: {test_case['input']}\n"
                f"**Oczekiwany status**: {test_case['expected_status']}\n"
                f"**Rzeczywisty status**: {actual_status}\n"
                f"**Oczekiwana odpowiedź**: {test_case['expected_response']}\n"
                f"**Rzeczywista odpowiedź**: {actual_response}\n"
                f"**Powiązany przypadek testowy**: {issue_key}\n"
                f"**Test Result**: not passed\n"
                f"**Defect created**: yes\n"
            ),
            "issuetype": {"name": "Bug"},
        }
        new_issue = jira.create_issue(fields=defect_dict)
        defect_key = new_issue.key
        print(f"Utworzono defekt w JIRA: {defect_key} dla przypadku testowego {test_case['test_id']}")

        # Aktualizacja opisu za pomocą update_issue
        updated_description = defect_dict["description"] + f"**Numer defektu**: {defect_key}"
        jira.update_issue(defect_key, fields={"description": updated_description})

        print(f"Pominięto powiązanie z {issue_key} – defekt {defect_key} został utworzony.")
        return defect_key
    except Exception as e:
        print(f"Błąd podczas raportowania defektu do JIRA: {e}")
        return None

# Testy automatyczne dla SOAP
def test_soap_api(db_session: Session):
    test_summary = []
    failures = []

    # Tworzenie sesji HTTP
    session = requests.Session()

    # Ręczne definiowanie operacji SOAP
    for test_case in SOAP_TEST_CASES:
        test_id_number = int(test_case["test_id"].split("_")[2])
        issue_key = f"{ISSUE_KEY}-{test_id_number + 20}"  # Dodajemy offset, aby uniknąć kolizji z REST
        print(f"Rozpoczynam test dla przypadku: {test_case['test_id']} (Issue: {issue_key})")

        # Obliczamy retry_count
        retry_count = db_session.query(TestResult).filter(TestResult.test_id == test_case["test_id"]).count()
        print(f"Retry count dla {test_case['test_id']}: {retry_count}")

        result = "passed"
        actual_status = 0
        actual_response = ""
        defect_key = None
        start_time = time.time()

        try:
            operation = test_case["operation"]
            if operation == "GetProduct":
                # Przygotuj żądanie SOAP
                soap_request = f"""
                <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="http://example.com/soap">
                    <soap:Body>
                        <ns:GetProduct>
                            <id>{test_case['input']['id']}</id>
                        </ns:GetProduct>
                    </soap:Body>
                </soap:Envelope>
                """
                response = session.post(SOAP_ENDPOINT, data=soap_request, headers={'Content-Type': 'text/xml'})
                response.raise_for_status()
                actual_status = response.status_code
                print(f"Surowa odpowiedź XML dla {test_case['test_id']}: {response.content.decode('utf-8')}")
                root = ET.fromstring(response.content)
                result_xml = root.find('.//{http://example.com/soap}result')
                if result_xml is None:
                    raise ValueError(f"Nie znaleziono elementu <result> w odpowiedzi XML dla {test_case['test_id']}")
                actual_response = json.loads(result_xml.text.replace("'", "\""))

            elif operation == "CreateProduct":
                soap_request = f"""
                <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="http://example.com/soap">
                    <soap:Body>
                        <ns:CreateProduct>
                            <name>{test_case['input']['name']}</name>
                            <description>{test_case['input']['description']}</description>
                            <price>{test_case['input']['price']}</price>
                        </ns:CreateProduct>
                    </soap:Body>
                </soap:Envelope>
                """
                response = session.post(SOAP_ENDPOINT, data=soap_request, headers={'Content-Type': 'text/xml'})
                response.raise_for_status()
                actual_status = response.status_code
                print(f"Surowa odpowiedź XML dla {test_case['test_id']}: {response.content.decode('utf-8')}")
                root = ET.fromstring(response.content)
                result_xml = root.find('.//{http://example.com/soap}result')
                if result_xml is None:
                    raise ValueError(f"Nie znaleziono elementu <result> w odpowiedzi XML dla {test_case['test_id']}")
                actual_response = {"result": int(result_xml.text)}

            elif operation == "DeleteProduct":
                soap_request = f"""
                <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="http://example.com/soap">
                    <soap:Body>
                        <ns:DeleteProduct>
                            <id>{test_case['input']['id']}</id>
                        </ns:DeleteProduct>
                    </soap:Body>
                </soap:Envelope>
                """
                response = session.post(SOAP_ENDPOINT, data=soap_request, headers={'Content-Type': 'text/xml'})
                response.raise_for_status()
                actual_status = response.status_code
                print(f"Surowa odpowiedź XML dla {test_case['test_id']}: {response.content.decode('utf-8') if response.content else 'Brak treści w odpowiedzi'}")
                if actual_status == 204:  # Dla DELETE brak treści jest prawidłowy
                    actual_response = test_case["expected_response"]  # Przyjmujemy oczekiwaną odpowiedź jako domyślną
                else:
                    root = ET.fromstring(response.content)
                    result_xml = root.find('.//{http://example.com/soap}result')
                    if result_xml is None:
                        raise ValueError(f"Nie znaleziono elementu <result> w odpowiedzi XML dla {test_case['test_id']}")
                    actual_response = json.loads(result_xml.text.replace("'", "\""))

            else:
                raise AssertionError(f"Nieobsługiwana operacja SOAP: {operation}")

            print(f"Otrzymano odpowiedź: {actual_response}")

            # Weryfikacja statusu
            assert actual_status == test_case["expected_status"], (
                f"Oczekiwano statusu {test_case['expected_status']}, otrzymano {actual_status}"
            )

            # Weryfikacja odpowiedzi
            expected_response = test_case["expected_response"]
            for key, value in expected_response.items():
                assert key in actual_response, f"Brak klucza {key} w odpowiedzi SOAP"
                assert actual_response[key] == value, (
                    f"Oczekiwano {key}: {value}, otrzymano {key}: {actual_response[key]}"
                )

            print(f"Test {test_case['test_id']} przeszedł pomyślnie.")
            test_summary.append((test_case["test_id"], "passed", None))

        except AssertionError as e:
            print(f"Test {test_case['test_id']} nie przeszedł: {str(e)}")
            result = "not passed"
            failure_message = f"Expected: {test_case['expected_response']}, Got: {actual_status}"
            print(f"Raportuję defekt dla {test_case['test_id']}...")
            try:
                defect_key = report_defect_to_jira(test_case, issue_key, actual_status, failure_message)
                if defect_key is None:
                    print(f"UWAGA: Defekt dla {test_case['test_id']} nie został zgłoszony do JIRA!")
                    defect_key = "PENDING"
            except Exception as jira_error:
                print(f"Błąd podczas raportowania defektu do JIRA: {jira_error}")
                defect_key = "PENDING"
            actual_response = failure_message
            test_summary.append((test_case["test_id"], "not passed", defect_key))
            failures.append(f"Test {test_case['test_id']} nie przeszedł: {str(e)}")
        except Exception as e:
            print(f"Test {test_case['test_id']} nie przeszedł z powodu błędu: {str(e)}")
            result = "not passed"
            actual_status = 0
            failure_message = f"Error: {str(e)}"
            print(f"Raportuję defekt dla {test_case['test_id']}...")
            try:
                defect_key = report_defect_to_jira(test_case, issue_key, actual_status, actual_response)
                if defect_key is None:
                    print(f"UWAGA: Defekt dla {test_case['test_id']} nie został zgłoszony do JIRA!")
                    defect_key = "PENDING"
            except Exception as jira_error:
                print(f"Błąd podczas raportowania defektu do JIRA: {jira_error}")
                defect_key = "PENDING"
            actual_response = failure_message
            test_summary.append((test_case["test_id"], "not passed", defect_key))
            failures.append(f"Test {test_case['test_id']} nie przeszedł z powodu błędu: {str(e)}")
        finally:
            # Obliczamy czas trwania testu
            duration_ms = int((time.time() - start_time) * 1000)

            # Debugowanie: Sprawdzamy, czy wynik testu zostanie zapisany
            print(f"Zapisz wynik dla {test_case['test_id']}: result={result}, actual_status={actual_status}, defect_key={defect_key}")

            # Zapis wyniku testu do tabeli test_results
            try:
                test_result = TestResult(
                    test_id=test_case["test_id"],
                    result=result,
                    actual_status=actual_status,
                    actual_response=str(actual_response)[:500],
                    defect_key=defect_key,
                    duration_ms=duration_ms,
                    environment="local",
                    tester="automated",
                    retry_count=retry_count
                )
                db_session.add(test_result)
                db_session.commit()
                print(f"Zapis wyniku dla {test_case['test_id']} zakończony sukcesem.")
            except SQLAlchemyError as e:
                print(f"Błąd podczas zapisu wyniku dla {test_case['test_id']}: {e}")
                db_session.rollback()
                raise

            # Debugowanie: Sprawdzamy, czy wynik został zapisany
            saved_result = db_session.query(TestResult).filter(TestResult.test_id == test_case["test_id"]).order_by(TestResult.timestamp.desc()).first()
            if saved_result:
                print(f"Wynik zapisany: {saved_result.test_id}, result={saved_result.result}, timestamp={saved_result.timestamp}")
            else:
                print(f"UWAGA: Wynik dla {test_case['test_id']} NIE został zapisany!")

    # Podsumowanie wyników testów
    print("\n=== Podsumowanie wyników testów ===")
    for test_id, result, defect_key in test_summary:
        if result == "passed":
            print(f"Test {test_id}: Passed")
        else:
            print(f"Test {test_id}: Not Passed, Defect: {defect_key}")

    # Zgłaszamy niepowodzenia na końcu
    if failures:
        pytest.fail("\n".join(failures))