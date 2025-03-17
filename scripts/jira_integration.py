from jira import JIRA
from sqlalchemy.orm import Session
from api.database.db_config import SessionLocal
from api.models.test_case import TestCase
from config import JIRA_SERVER, JIRA_USERNAME, JIRA_API_TOKEN, JIRA_PROJECT_KEY

# Połączenie z JIRA
jira = JIRA(
    server=JIRA_SERVER,
    basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN)
)

def import_test_cases_to_jira():
    # Otwieramy sesję bazy danych
    db: Session = SessionLocal()
    try:
        # Pobieramy wszystkie przypadki testowe z tabeli test_cases
        test_cases = db.query(TestCase).all()
        print(f"Znaleziono {len(test_cases)} przypadków testowych do zaimportowania do JIRA.")

        # Dla każdego przypadku testowego tworzymy issue w JIRA
        for test_case in test_cases:
            # Sprawdzamy, czy przypadek testowy już istnieje w JIRA (na podstawie test_id w summary)
            jql_query = f'project={JIRA_PROJECT_KEY} AND summary ~ "{test_case.test_id}"'
            existing_issues = jira.search_issues(jql_query)
            if existing_issues:
                print(f"Przypadek testowy {test_case.test_id} już istnieje w JIRA, pomijam.")
                continue

            # Tworzymy nowy issue w JIRA
            issue_dict = {
                "project": {"key": JIRA_PROJECT_KEY},
                "summary": f"{test_case.test_id}: {test_case.description}",
                "description": (
                    f"**Endpoint**: {test_case.endpoint}\n"
                    f"**Method**: {test_case.method}\n"
                    f"**Test Type**: {test_case.test_type}\n"
                    f"**Expected Status**: {test_case.expected_status}\n"
                    f"**Expected Response**: {test_case.expected_response}"
                ),
                "issuetype": {"name": "Task"},  # Zmieniono z "Test" na "Task"
            }
            new_issue = jira.create_issue(fields=issue_dict)
            print(f"Utworzono issue w JIRA: {new_issue.key} dla przypadku testowego {test_case.test_id}")

    except Exception as e:
        print(f"Wystąpił błąd podczas importu do JIRA: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import_test_cases_to_jira()