from jira import JIRA
from config import JIRA_SERVER, JIRA_USERNAME, JIRA_API_TOKEN, JIRA_PROJECT_KEY


def test_jira_connection():
    try:
        jira = JIRA(
            server=JIRA_SERVER,
            basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN)
        )
        print("Połączenie z JIRA powiodło się!")

        # Sprawdzamy, czy projekt istnieje
        project = jira.project(JIRA_PROJECT_KEY)
        print(f"Projekt {JIRA_PROJECT_KEY} istnieje: {project.name}")

        # Testowe wyszukiwanie zgłoszeń
        issues = jira.search_issues(f'project={JIRA_PROJECT_KEY}')
        print(f"Znaleziono {len(issues)} zgłoszeń w projekcie {JIRA_PROJECT_KEY}")
    except Exception as e:
        print(f"Błąd połączenia z JIRA: {e}")


if __name__ == "__main__":
    test_jira_connection()