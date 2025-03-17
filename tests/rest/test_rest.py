import pytest
import requests
import json
import time
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from jira import JIRA
from api.database.db_config import SessionLocal
from api.models.test_case import TestCase
from api.models.test_result import TestResult
from config import JIRA_SERVER, JIRA_USERNAME, JIRA_API_TOKEN, JIRA_PROJECT_KEY, ISSUE_KEY

# Baza URL dla API
BASE_URL = "http://127.0.0.1:8000"

# Połączenie z JIRA
jira = JIRA(
    server=JIRA_SERVER,
    basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN)
)

# Dodajemy opcje do pytest
def pytest_addoption(parser):
    parser.addoption(
        "--test-ids",
        action="store",
        default=None,
        help="Comma-separated list of test IDs to run (e.g., TC_001,TC_002)"
    )
    parser.addoption(
        "--run-failed",
        action="store_true",
        default=False,
        help="Run only tests that failed in the last run"
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

@pytest.fixture
def test_cases(db_session: Session, request):
    # Bezpieczne pobieranie opcji z pytest
    test_ids = None
    run_failed = False
    try:
        test_ids = request.config.getoption("--test-ids", default=None)
        run_failed = request.config.getoption("--run-failed", default=False)
    except ValueError:
        print("Opcje --test-ids lub --run-failed nie zostały zdefiniowane, używam domyślnych wartości.")

    # Pobieramy wszystkie przypadki testowe
    query = db_session.query(TestCase)

    # Filtrujemy testy na podstawie --test-ids
    if test_ids:
        test_ids_list = [tid.strip() for tid in test_ids.split(",")]
        print(f"Filtruję testy dla test_ids: {test_ids_list}")
        query = query.filter(TestCase.test_id.in_(test_ids_list))

    # Filtrujemy testy na podstawie --run-failed
    elif run_failed:
        # Pobieramy test_id testów, które nie przeszły w ostatniej próbie
        failed_tests = (
            db_session.query(TestResult.test_id)
            .filter(TestResult.result == "not passed")
            .distinct()
            .all()
        )
        failed_test_ids = [test_id for (test_id,) in failed_tests]
        if not failed_test_ids:
            print("Brak testów, które nie przeszły w ostatniej próbie.")
            return []
        print(f"Filtruję testy dla test_ids, które nie przeszły: {failed_test_ids}")
        query = query.filter(TestCase.test_id.in_(failed_test_ids))

    test_cases = query.all()
    print(f"Wybrane testy do uruchomienia: {[tc.test_id for tc in test_cases]}")
    return test_cases

# Funkcja do raportowania defektów w JIRA
def report_defect_to_jira(test_case: TestCase, issue_key: str, actual_status: int, actual_response: str):
    try:
        print(f"Szukam istniejących defektów w JIRA dla {test_case.test_id}...")
        jql_query = f'project={JIRA_PROJECT_KEY} AND issuetype=Bug AND summary ~ "Defekt dla {test_case.test_id}"'
        existing_defects = jira.search_issues(jql_query)
        print(f"Znaleziono {len(existing_defects)} istniejących defektów")

        if existing_defects:
            defect = existing_defects[0]
            defect_key = defect.key
            comment = (
                f"Retest dla przypadku testowego {test_case.test_id}:\n"
                f"**Rzeczywisty status**: {actual_status}\n"
                f"**Rzeczywista odpowiedź**: {actual_response}\n"
                f"**Test Result**: not passed\n"
                f"**Defect created**: yes\n"
                f"**Numer defektu**: {defect_key}"
            )
            jira.add_comment(defect_key, comment)
            print(f"Dodano komentarz do istniejącego defektu {defect_key} dla przypadku testowego {test_case.test_id}")
            return defect_key

        print(f"Tworzę nowy defekt w JIRA dla {test_case.test_id}...")
        defect_dict = {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": f"Defekt dla {test_case.test_id}: {test_case.description}",
            "description": (
                f"**Przypadek testowy**: {test_case.test_id}\n"
                f"**Endpoint**: {test_case.endpoint}\n"
                f"**Method**: {test_case.method}\n"
                f"**Oczekiwany status**: {test_case.expected_status}\n"
                f"**Rzeczywisty status**: {actual_status}\n"
                f"**Oczekiwana odpowiedź**: {test_case.expected_response}\n"
                f"**Rzeczywista odpowiedź**: {actual_response}\n"
                f"**Powiązany przypadek testowy**: {issue_key}\n"
                f"**Test Result**: not passed\n"
                f"**Defect created**: yes\n"
            ),
            "issuetype": {"name": "Bug"},
        }
        new_issue = jira.create_issue(fields=defect_dict)
        defect_key = new_issue.key
        print(f"Utworzono defekt w JIRA: {defect_key} dla przypadku testowego {test_case.test_id}")

        updated_description = defect_dict["description"] + f"**Numer defektu**: {defect_key}"
        jira.update_issue_field(defect_key, {"description": updated_description})

        jira.create_issue_link(
            type="Relates",
            inwardIssue=new_issue.key,
            outwardIssue=issue_key
        )
        print(f"Powiązano defekt {defect_key} z przypadkiem testowym {issue_key}")
        return defect_key
    except Exception as e:
        print(f"Błąd podczas raportowania defektu do JIRA: {e}")
        return None

# Testy automatyczne
def test_rest_api(test_cases, db_session: Session):
    if not test_cases:
        print("Brak testów do uruchomienia.")
        return

    test_summary = []
    failures = []

    for test_case in test_cases:
        test_id_number = int(test_case.test_id.split("_")[1])
        issue_key = f"{ISSUE_KEY}-{test_id_number}"
        print(f"Rozpoczynam test dla przypadku: {test_case.test_id} (Issue: {issue_key})")

        # Obliczamy retry_count – liczba poprzednich prób dla tego test_id
        retry_count = db_session.query(TestResult).filter(TestResult.test_id == test_case.test_id).count()
        print(f"Retry count dla {test_case.test_id}: {retry_count}")

        url = BASE_URL + test_case.endpoint
        method = test_case.method.lower()
        data = None
        if test_case.method in ["POST", "PUT"]:
            if test_case.test_id in ["TC_007", "TC_009", "TC_015", "TC_017", "TC_020"]:
                data = {
                    "name": "Test Product",
                    "description": "Test Description",
                    "price": 99.99,
                    "available": True,
                    "stock": 10
                }
                if test_case.test_id == "TC_015":
                    data["price"] = 0
                elif test_case.test_id == "TC_017":
                    data["price"] = 9999999.99
            elif test_case.test_id == "TC_008":
                data = {
                    "description": "Test Description",
                    "price": 99.99
                }
            elif test_case.test_id == "TC_016":
                data = {
                    "name": "Test Product",
                    "description": "Test Description",
                    "price": -10
                }
            elif test_case.test_id == "TC_018":
                data = {
                    "name": "A" * 101,
                    "description": "Test Description",
                    "price": 99.99
                }

        response = None
        result = "passed"
        actual_status = 0
        actual_response = ""
        defect_key = None
        start_time = time.time()

        try:
            if method == "get":
                print(f"Wysyłam żądanie GET na {url}")
                response = requests.get(url)
            elif method == "post":
                print(f"Wysyłam żądanie POST na {url} z danymi: {data}")
                response = requests.post(url, json=data)
            elif method == "put":
                print(f"Wysyłam żądanie PUT na {url} z danymi: {data}")
                response = requests.put(url, json=data)
            elif method == "delete":
                print(f"Wysyłam żądanie DELETE na {url}")
                response = requests.delete(url)
            else:
                raise AssertionError(f"Nieobsługiwana metoda HTTP: {method}")

            actual_status = response.status_code
            actual_response = response.text

            print(f"Otrzymano status: {actual_status}, odpowiedź: {actual_response[:100]}...")
            assert response.status_code == test_case.expected_status, (
                f"Oczekiwano statusu {test_case.expected_status}, otrzymano {response.status_code}"
            )

            if test_case.expected_response:
                try:
                    expected_response = json.loads(test_case.expected_response)
                    actual_response_json = response.json()
                    if isinstance(expected_response, dict):
                        for key, value in expected_response.items():
                            assert key in actual_response_json, f"Brak klucza {key} w odpowiedzi API"
                            assert actual_response_json[key] == value, (
                                f"Oczekiwano {key}: {value}, otrzymano {key}: {actual_response_json[key]}"
                            )
                    else:
                        assert actual_response_json == expected_response, (
                            f"Oczekiwano odpowiedzi {expected_response}, otrzymano {actual_response_json}"
                        )
                    actual_response = json.dumps(actual_response_json, ensure_ascii=False)[:500]
                except json.JSONDecodeError:
                    assert response.text == test_case.expected_response, (
                        f"Oczekiwano odpowiedzi {test_case.expected_response}, otrzymano {response.text}"
                    )
                    actual_response = response.text[:500]

            print(f"Test {test_case.test_id} przeszedł pomyślnie.")
            test_summary.append((test_case.test_id, "passed", None))

        except AssertionError as e:
            print(f"Test {test_case.test_id} nie przeszedł: {str(e)}")
            result = "not passed"
            failure_message = f"Expected: {test_case.expected_response}, Got: {actual_status}"
            print(f"Raportuję defekt dla {test_case.test_id}...")
            try:
                defect_key = report_defect_to_jira(test_case, issue_key, actual_status, failure_message)
                if defect_key is None:
                    print(f"UWAGA: Defekt dla {test_case.test_id} nie został zgłoszony do JIRA!")
                    defect_key = "PENDING"
            except Exception as jira_error:
                print(f"Błąd podczas raportowania defektu do JIRA: {jira_error}")
                defect_key = "PENDING"
            actual_response = failure_message[:500]
            test_summary.append((test_case.test_id, "not passed", defect_key))
            failures.append(f"Test {test_case.test_id} nie przeszedł: {str(e)}")
        except Exception as e:
            print(f"Test {test_case.test_id} nie przeszedł z powodu błędu: {str(e)}")
            result = "not passed"
            actual_status = getattr(response, 'status_code', 0)
            failure_message = f"Error: {str(e)}"
            print(f"Raportuję defekt dla {test_case.test_id}...")
            try:
                defect_key = report_defect_to_jira(test_case, issue_key, actual_status, actual_response)
                if defect_key is None:
                    print(f"UWAGA: Defekt dla {test_case.test_id} nie został zgłoszony do JIRA!")
                    defect_key = "PENDING"
            except Exception as jira_error:
                print(f"Błąd podczas raportowania defektu do JIRA: {jira_error}")
                defect_key = "PENDING"
            actual_response = failure_message[:500]
            test_summary.append((test_case.test_id, "not passed", defect_key))
            failures.append(f"Test {test_case.test_id} nie przeszedł z powodu błędu: {str(e)}")
        finally:
            # Obliczamy czas trwania testu
            duration_ms = int((time.time() - start_time) * 1000)

            # Debugowanie: Sprawdzamy, czy wynik testu zostanie zapisany
            print(f"Zapisz wynik dla {test_case.test_id}: result={result}, actual_status={actual_status}, defect_key={defect_key}")

            # Zapis wyniku testu do tabeli test_results
            try:
                test_result = TestResult(
                    test_id=test_case.test_id,
                    result=result,
                    actual_status=actual_status,
                    actual_response=actual_response,
                    defect_key=defect_key,
                    duration_ms=duration_ms,
                    environment="local",
                    tester="automated",
                    retry_count=retry_count
                )
                db_session.add(test_result)
                db_session.commit()
                print(f"Zapis wyniku dla {test_case.test_id} zakończony sukcesem.")
            except SQLAlchemyError as e:
                print(f"Błąd podczas zapisu wyniku dla {test_case.test_id}: {e}")
                db_session.rollback()
                raise

            # Debugowanie: Sprawdzamy, czy wynik został zapisany
            saved_result = db_session.query(TestResult).filter(TestResult.test_id == test_case.test_id).order_by(TestResult.timestamp.desc()).first()
            if saved_result:
                print(f"Wynik zapisany: {saved_result.test_id}, result={saved_result.result}, timestamp={saved_result.timestamp}")
            else:
                print(f"UWAGA: Wynik dla {test_case.test_id} NIE został zapisany!")

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