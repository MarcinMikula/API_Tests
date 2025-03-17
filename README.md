It was supposed to be just learning Python FastApi, but in parallel I started to learn Artificial Intelligence and eventually, in addition to FastApi, we also have SQLAlchemy, Requests, PyTest, JIRA.
But in reality it's still a hull and there's a lot to improve and even more to add :)

# Project API Tests

This repository contains an automated testing framework for API services, focusing on both SOAP and REST protocols. The project is designed to validate API endpoints, integrate with JIRA for defect tracking, and manage test results using a local database.

## Overview

The `project-api-tests` repository is a Python-based solution for testing SOAP and REST APIs. It includes a custom SOAP server, automated test scripts, and integration with external tools like JIRA and Postman/Newman. The project is suitable for developers and QA engineers looking to automate API testing workflows.

## Features

- **SOAP API Testing**: Automated tests for SOAP endpoints using `test_soap.py`.
- **REST API Testing**: Support for REST API validation (to be expanded).
- **JIRA Integration**: Test cases and defects are managed via a CSV file and synced with JIRA.
- **Database Management**: Test results are stored in a local database (e.g., SQLite).
- **Postman Collection**: Includes `SOAP_API_Tests.json` for manual and automated testing with Newman.
- **Environment Management**: Uses `python-decouple` to handle sensitive configurations securely.

## Components

### 1. SOAP Server
- Implemented in `soap_server.py`.
- Runs on `http://127.0.0.1:8002/soap/`.
- Provides endpoints for `GetProduct`, `CreateProduct`, and `DeleteProduct` operations.
- Uses a simple in-memory data store (to be replaced with a persistent database in future iterations).

### 2. Database
- Test results are stored in a local database (e.g., SQLite table `test_results`).
- Structure includes columns: `id`, `test_case`, `result`, `actual_status`, `actual_response`, `timestamp`, `retry_count`, `environment`, `test_type`, `defect_key`.
- Example data:
  - `SOAP_TC_001`: `passed`, `200`, `{'id': 1, 'name': 'Laptop', 'description': 'Laptop gamingowy'}`
  - `SOAP_TC_002`: `passed`, `201`, `{'result': 21}`
  - `SOAP_TC_003`: `passed`, `204`, `{'status': 'Product deleted'}`

### 3. JIRA Integration
- Integrates with JIRA for defect tracking and test case management.
- Test cases are defined in a CSV file (e.g., `test_cases.csv`), with columns like `test_case_id`, `description`, `expected_status`, `endpoint`.
- Example `test_cases.csv`:
- Defects are reported to JIRA with keys like `SCRUM-21`, `SCRUM-22`, etc., when tests fail.
- Requires JIRA API token and credentials (stored in `.env`).

### 4. Test Types
- **SOAP Tests**: Implemented using Python with `test_soap.py`. Validates XML responses and HTTP status codes.
- **REST Tests**: Currently in development. Planned to include REST API endpoints with similar validation logic.
- Tests are automated and can be run via Newman or directly with Python.

## Setup

Follow these steps to set up and run the project locally:

### Prerequisites
- **Python 3.x**
- **Node.js** and **Newman** (for Postman collection execution)
- **Git** (for cloning the repository)

### Installation
1. **Clone the repository**:
 ```bash
 git clone https://github.com/MarcinMikula/project-api-tests.git
 cd project-api-tests

Install Python dependencies:
Create a virtual environment (optional but recommended):
bash

python -m venv .venv
.\.venv\Scripts\activate  # Windows

Install required packages:
bash

pip install python-decouple

Install Newman:
bash

npm install -g newman

Configure environment variables:
Create a .env file in the root directory:

JIRA_SERVER=https://twoja-instancja.atlassian.net
JIRA_USERNAME=twój.email@example.com
JIRA_API_TOKEN=twój-token-api
JIRA_PROJECT_KEY=SCRUM
ISSUE_KEY=SCRUM
SOAP_ENDPOINT=http://127.0.0.1:8002/soap/

Ensure .env is listed in .gitignore to avoid committing sensitive data.

Run the SOAP server:
bash

python soap_server.py

Running Tests
Python Tests:
Run the test script directly:
bash

python tests/soap/test_soap.py

Newman Tests:
Execute the Postman collection:
bash

newman run SOAP_API_Tests.json -e Local_SOAP_Environment.json

