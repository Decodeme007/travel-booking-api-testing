# 🛫 Travel Booking API Automation & Testing Framework

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Test Framework](https://img.shields.io/badge/Testing-Pytest%20%2B%20Requests-green.svg)](https://docs.pytest.org/)
[![API Backend](https://img.shields.io/badge/API-FastAPI%20%2B%20Uvicorn-009688.svg)](https://fastapi.tiangolo.com/)
[![Database](https://img.shields.io/badge/Database-SQLite%20%2F%20MySQL%20(SQLAlchemy)-orange.svg)](https://www.sqlalchemy.org/)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF.svg)](https://github.com/features/actions)
[![Test Status](https://img.shields.io/badge/Tests-61%2F61%20Passed-brightgreen.svg)]()

> A production-grade, simulated travel booking backend system and an automated API test engineering framework built with an **SDET mindset**. It validates RESTful microservices across positive, negative, boundary, and regression scenarios, with deep SQL database consistency validation, JSON schema enforcement, and CI/CD automation.

---

## 📌 Resume Highlights & Impact

- **Automated API Testing Framework**: Developed an end-to-end automated testing framework using Python, Pytest, and Requests following the **Service Object Pattern** to validate RESTful travel booking services.
- **Exhaustive Test Coverage**: Designed and executed **61 automated test cases** spanning positive, negative, boundary, and regression scenarios across Flight Search, Hotel Search, Booking Creation, Payment Processing, Booking Status, and Cancellation workflows.
- **Multilayered Validation**: Validated HTTP status codes (200, 201, 400, 401, 402, 403, 404, 409, 422), JSON schemas (`jsonschema`), response time latency (<1500ms SLA), and database consistency via direct SQL queries.
- **Database & State Integrity Testing**: Implemented SQL query verifications using SQLAlchemy to assert data persistence, seat/room inventory decrements upon booking, and automatic seat restoration upon cancellation.
- **Postman & CI/CD Integration**: Engineered a complete Postman Collection with automated test scripts and environment variables, alongside a GitHub Actions CI pipeline running tests on every push with HTML report artifact generation.

---

## 🏗️ Project Architecture

```
+-----------------------------------------------------------------------------------+
|                            TRAVEL BOOKING REST APIs                               |
|                                                                                   |
|   +-------------------+  +-------------------+  +------------------------------+   |
|   |  Flight Search    |  |   Hotel Search    |  |  Booking & Cancellation      |   |
|   |  /flights/search  |  |   /hotels/search  |  |  /bookings, /status, /cancel |   |
|   +-------------------+  +-------------------+  +------------------------------+   |
|                           +------------------+  +------------------------------+   |
|                           |  Payment Gateway |  |  Authentication (JWT)       |   |
|                           |  /payments       |  |  /auth/login, /auth/register |   |
|                           +------------------+  +------------------------------+   |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|                        AUTOMATED TESTING FRAMEWORK (SDET)                         |
|                                                                                   |
|  +---------------------+  +----------------------+  +--------------------------+  |
|  | Service Object API  |  | Custom Assertion Hub |  | Database Query Helper    |  |
|  | Clients (Requests)  |  | (Status, Schema, SLA)|  | (SQL Data Consistency)   |  |
|  +---------------------+  +----------------------+  +--------------------------+  |
|                                                                                   |
|  +---------------------+  +----------------------+  +--------------------------+  |
|  | JSON Schemas        |  | Dynamic Synthetic    |  | Pytest Fixtures &        |  |
|  | (Draft-07 Validator)|  | Test Data Generators |  | Session Lifecycle        |  |
|  +---------------------+  +----------------------+  +--------------------------+  |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|                       EXECUTION, REPORTS & CI/CD AUTOMATION                       |
|                                                                                   |
|     +-------------------------+            +---------------------------------+    |
|     | HTML Reports            |            | GitHub Actions CI Pipeline      |    |
|     | (Passed, Failed, Logs)  |            | (Continuous Regression Testing) |    |
|     +-------------------------+            +---------------------------------+    |
|     +-------------------------+            +---------------------------------+    |
|     | Postman Test Collection |            | Structured Execution Logs       |    |
|     | (Newman / GUI Runner)   |            | (File & Console Logging)        |    |
|     +-------------------------+            +---------------------------------+    |
+-----------------------------------------------------------------------------------+
```

---

## 🎯 What Exactly Is Tested? (SDET Test Matrix)

| Module / API | Test Scenarios | Status Codes | Validation Layer |
| :--- | :--- | :--- | :--- |
| **Authentication** | Valid login, invalid password, non-existent user, JWT profile inspection, missing token, invalid token, expired token simulation, user registration, duplicate registration | `200`, `201`, `401`, `409` | Status, JWT Claims, JSON Schema |
| **Flight Search** | Valid search, round-trip with return date, missing origin/destination, past departure date, return date before departure, invalid date formats (`YYYY/MM/DD`, strings), same origin & destination, invalid IATA airport codes, boundary passenger counts (0, -1, 11), flight by ID, 404 not found | `200`, `400`, `404`, `422` | Status, JSON Schema, Latency SLA (<1500ms) |
| **Hotel Search** | Valid search by city, invalid numeric city, check-out before check-in, check-in equals check-out, past check-in date, missing parameters, guest boundary limits (0, -1, 15), hotel details by ID, 404 not found | `200`, `400`, `404`, `422` | Status, JSON Schema, Content assertions |
| **Booking Creation** | Flight booking creation, hotel booking creation, duplicate booking with idempotency key, invalid/non-existent flight ID, unsupported booking type, unauthorized access | `201`, `400`, `401`, `404`, `409`, `422` | Status, JSON Schema, **Direct SQL: Booking record created & flight seat decrement** |
| **Payment Simulation** | Successful payment, card decline simulation (`4000000000000002`), mismatched booking amount, negative/zero amounts, paying already confirmed booking, payment for non-existent booking | `200`, `400`, `402`, `404` | Status, JSON Schema, **Direct SQL: Payment record created & booking transitions to CONFIRMED** |
| **Cancellation** | Cancel pending booking, cancel confirmed booking with full refund, inventory restoration, cancel already cancelled booking (double cancellation), non-existent booking | `200`, `400`, `404` | Status, JSON Schema, **Direct SQL: Cancellation record created & flight seats restored** |
| **Booking Status** | Full lifecycle status transition (`PENDING` -> `CONFIRMED` -> `CANCELLED`), admin access authorization, 404 not found | `200`, `404` | Status, Schema, Status field consistency |
| **E2E Workflow** | Search Flight -> Select Flight -> Book for 2 -> DB Seat Check -> Process Payment -> DB Confirmed Check -> Cancel Booking -> DB Inventory Restoration Check | `200`, `201` | Full End-to-End Regression Cycle |

---

## 📁 Repository Structure

```
d:\testing\
├── app/                                 # Simulated Travel Booking Backend (FastAPI)
│   ├── __init__.py
│   ├── config.py                        # App & JWT configuration
│   ├── database.py                      # SQLAlchemy database session & engine
│   ├── models.py                        # ORM models (User, Flight, Hotel, Booking, Payment, Cancellation)
│   ├── schemas.py                       # Pydantic validation schemas
│   ├── auth.py                          # JWT token encoding/decoding & dependency injection
│   ├── seed_data.py                     # Initial realistic seed data for Flights, Hotels, and Users
│   ├── main.py                          # FastAPI application & middleware
│   └── routes/
│       ├── auth_routes.py               # /api/v1/auth endpoints
│       ├── flight_routes.py             # /api/v1/flights endpoints
│       ├── hotel_routes.py              # /api/v1/hotels endpoints
│       ├── booking_routes.py            # /api/v1/bookings endpoints
│       └── payment_routes.py            # /api/v1/payments endpoints
├── framework/                           # Reusable Automation Testing Framework Core
│   ├── __init__.py
│   ├── config.py                        # Framework configuration (Base URL, DB path, SLAs)
│   ├── api_clients/                     # Service Object Pattern
│   │   ├── base_client.py               # Custom HTTP Client (logging, latency, auth)
│   │   ├── auth_client.py               # Auth API service client
│   │   ├── flight_client.py             # Flight API service client
│   │   ├── hotel_client.py              # Hotel API service client
│   │   ├── booking_client.py            # Booking API service client
│   │   └── payment_client.py            # Payment API service client
│   ├── database/
│   │   └── db_helper.py                 # Direct SQL execution & consistency verification helper
│   ├── schemas/                         # JSON Schemas (Draft-07) for response validation
│   │   ├── auth_schema.py
│   │   ├── flight_schema.py
│   │   ├── hotel_schema.py
│   │   ├── booking_schema.py
│   │   └── payment_schema.py
│   └── utils/
│       ├── logger.py                    # Dual console & file structured logger
│       ├── data_generator.py            # Dynamic test data generation (dates, strings, emails)
│       └── assertions.py                # Reusable custom assertion methods
├── tests/                               # SDET Pytest Test Suites
│   ├── conftest.py                      # Fixtures (auto-server launch, tokens, DB helpers)
│   ├── test_auth.py                     # Authentication & Authorization test scenarios
│   ├── test_flight_search.py            # Flight search positive/negative/boundary tests
│   ├── test_hotel_search.py             # Hotel search positive/negative/boundary tests
│   ├── test_booking.py                  # Booking creation & duplicate prevention tests
│   ├── test_payment.py                  # Payment simulation & failure tests
│   ├── test_cancellation.py             # Cancellation & inventory restoration tests
│   ├── test_booking_status.py           # Lifecycle status verification tests
│   └── test_e2e_booking_workflow.py     # Complete End-to-End User Journey test
├── postman/
│   ├── Travel_Booking_API.postman_collection.json       # Exported Postman collection with tests
│   └── Travel_Booking_Environment.postman_environment.json # Postman local environment
├── .github/
│   └── workflows/
│       └── api-tests.yml                # GitHub Actions Continuous Testing pipeline
├── reports/                             # Automated Test Reports & Logs
│   ├── test_report.html                 # Pytest HTML Test Report with full diagnostics
│   └── logs/
│       └── test_execution.log           # Verbose API request/response execution log
├── pytest.ini                           # Pytest configuration
├── requirements.txt                     # Python dependencies
├── run_server.py                        # Standalone API server runner
├── run_tests.py                         # Single-command test executor & report generator
└── README.md                            # Complete Project Documentation
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10 or higher
- Git

### 2. Installation
```bash
# Clone the repository
git clone <repo-url>
cd travel-booking-api-framework

# Install dependencies
pip install -r requirements.txt
```

### 3. Seed Database
Initialize SQLite schema and populate realistic flight routes, hotel listings, and test users:
```bash
python -m app.seed_data
```

### 4. Running the API Server (Optional for manual exploration)
```bash
python run_server.py
```
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc API Documentation: `http://127.0.0.1:8000/redoc`

---

## 🧪 Executing the Automated Test Suite

The test framework features an auto-managed server lifecycle: running the test suite will automatically spin up the test server, execute all suites, validate SQL states, and generate interactive HTML reports.

### Run All 61 Test Scenarios
```bash
python run_tests.py
```
*Or using Pytest directly:*
```bash
pytest tests/ -v --html=reports/test_report.html --self-contained-html
```

### Run Specific Test Modules
```bash
# Flight search tests
pytest tests/test_flight_search.py -v

# Database consistency & booking tests
pytest tests/test_booking.py -v

# Payment simulation tests
pytest tests/test_payment.py -v

# End-to-End full user journey
pytest tests/test_e2e_booking_workflow.py -v
```

---

## 📊 Automated Test Reports & Logs

1. **Interactive HTML Report**: Open `reports/test_report.html` in any web browser to view pass/fail metrics, execution timings, and assertions.
2. **Execution Logs**: Detailed HTTP request bodies, headers, response status, payloads, and SQL queries are logged in `reports/logs/test_execution.log`.

---

## 📬 Postman Collection & Automated Scripts

A complete Postman test suite is provided under the `postman/` directory:
1. Import `postman/Travel_Booking_API.postman_collection.json` into Postman.
2. Import `postman/Travel_Booking_Environment.postman_environment.json`.
3. Set the active environment to **Travel Booking Environment (Local)**.
4. Execute the collection runner — token chaining and dynamic IDs are automatically handled via Postman test scripts.

---

## ⚙️ GitHub Actions CI/CD Pipeline

The `.github/workflows/api-tests.yml` workflow automatically runs the entire test suite on every `git push` or `pull_request`:
1. Sets up Python 3.10 environment.
2. Installs requirements and seeds the database.
3. Runs the 61 automated Pytest test cases.
4. Generates and uploads the self-contained HTML test report and execution logs as build artifacts available for download.

---

## 🗄️ Database Testing & SQL Verification Highlights

In addition to validating HTTP responses, this framework enforces backend state integrity:
- **Seat Deduction**: When a user books 2 seats on Flight `AA-101`, direct SQL queries verify that `available_seats` in table `flights` is reduced by exactly 2.
- **Payment Reconciliation**: When payment succeeds, SQL verification ensures a record exists in `payments` with matching `amount` and status `SUCCESS`, and that `bookings.status` transitions to `CONFIRMED`.
- **Inventory Restoration**: When a confirmed booking is cancelled, SQL queries confirm that the reserved seats are credited back to `flights.available_seats`, and a refund record is generated in `cancellations`.

---

## 👨‍💻 Developed with SDET Best Practices
- **Page Object / Service Object Pattern**: Decoupled HTTP logic from test assertions.
- **Strict JSON Schema Validation**: Uses Draft-07 schemas to catch contract breakages.
- **Response Time SLA Verification**: Every endpoint is asserted against latency thresholds.
- **Data-Driven & Parameterized Testing**: Boundary and negative inputs tested with `@pytest.mark.parametrize`.
- **Clean Fixture Architecture**: Modular scoped Pytest fixtures in `conftest.py`.
