# Vendora - Detailed Project README

Vendora is a full-stack service marketplace web app where customers can discover vendors, book appointments, leave reviews, and get AI-powered recommendations. Vendors can manage business profiles, services, appointments, analytics, and review insights.

The project is built primarily with Flask + MySQL and integrates two ML services hosted separately:
- Sentiment analysis API for classifying customer review text
- Recommendation API for personalized vendor suggestions

---

## 1) Project Structure

```text
vendora2/
|-- vendora_app/                     # Main Flask application
|   |-- app.py                       # App factory, config, blueprint registration
|   |-- extensions.py                # Flask extensions (SQLAlchemy, LoginManager, Bcrypt)
|   |-- blueprints/
|   |   |-- auth/                    # Signup/login/profile/delete account
|   |   |-- customer/                # Customer dashboard, booking actions, recommendations
|   |   |-- vendor/                  # Vendor profile, services, appointments, analytics
|   |   |-- appointment/             # Booking flow and slot conflict handling
|   |   `-- core/                    # Root routes and static pages
|   `-- migrations/                  # Alembic/Flask-Migrate migration files
|
|-- Sentiment Analysis/              # FastAPI + DistilBERT sentiment microservice
|-- Recommendation System/           # Recommender experimentation assets (notebook + data)
|-- run.py                           # Flask app entry point
|-- requirements.txt                 # Main Flask app dependencies
`-- README2.md                       # This file
```

---

## 2) Core Features

### Customer
- Browse vendors and search by business name
- View vendor details and service catalog
- Book appointments with conflict checks (overlapping slots are blocked)
- Update or cancel existing appointments
- Rate completed appointments and submit text reviews
- Get AI-powered vendor recommendations

### Vendor
- Complete and update vendor business profile
- Upload business images via Cloudinary
- Create, edit, and delete offered services
- Manage appointment lifecycle (`pending` -> `confirmed` -> `completed` / `cancelled`)
- View dashboard and analytics (revenue, customers, service demand trends)
- Track review sentiment breakdown (`positive`, `neutral`, `negative`)

### Authentication and Accounts
- Role-based signup/login (`customer`, `vendor`, or both)
- Password hashing via Flask-Bcrypt
- User profile updates (name + profile image)
- Account deletion with cascade behavior for linked profiles

### AI Integration
- **Sentiment API**: review text is classified before storing sentiment in appointments
- **Recommendation API**: customer ID is sent to external recommender service and vendor IDs are mapped back to local DB records

---

## 3) Tech Stack

### Main App
- Flask 3
- Flask-SQLAlchemy
- Flask-Migrate + Alembic
- Flask-Login
- Flask-Bcrypt
- MySQL (via PyMySQL driver)
- Jinja2 templates
- Cloudinary (image hosting)

### ML/AI Services
- FastAPI (Sentiment service)
- Hugging Face Transformers + PyTorch (DistilBERT inference)
- External recommender endpoint (hosted service consumed by Flask app)

---

## 4) Data Model Overview

### `User`
- Identity and auth fields (`username`, `password`)
- Role flags (`is_customer`, `is_vendor`, `last_role`)
- Profile media (`profile_img`, `business_imgs`)
- One-to-one with `Customer` and `Vendor`

### `Customer`
- Personal profile data (`full_name`, `address`, `phone`, `age`, `gender`, `city`)

### `Vendor`
- Business profile data (`business_name`, `business_address`, contacts, payments)
- Aggregate rating fields (`rating`, `rater_no`)
- One-to-many with `Service`

### `Service`
- Service metadata (`service_name`, `service_type`, `duration_minutes`, `service_cost`)

### `Appointment`
- Links customer/vendor/service
- Time window (`start_time`, `end_time`)
- Status (`pending`, `confirmed`, `cancelled`, `completed`)
- Review metadata (`rating`, `review`, `sentiment`)

---

## 5) Route Map (High-Level)

### Core
- `/` -> redirects to vendor listing page
- `/about`
- `/developer`

### Auth (`/auth`)
- `/signup`, `/login`, `/logout`
- `/profile_update`
- `/delete_account`

### Customer (`/customer`)
- `/homepage` vendor listing/search
- `/profile_setup`, `/dashboard`
- `/vendor/<vendor_id>`
- `/appointments`
- `/update-appointment/<id>`, `/cancel-appointment/<id>`
- `/rate/<appointment_id>`
- `/recommendation`

### Vendor (`/vendor`)
- `/profile_setup`, `/profile_update`
- `/services`, `/add-service`, `/edit-service/<id>`, `/delete-service/<id>`
- `/dashboard`, `/appointments`
- `/confirm-appointment/<id>`, `/cancel-appointment/<id>`, `/complete_appointment/<id>`
- `/analytics`, `/reviews`, `/support`

### Appointment (`/appointment`)
- `/book/<service_id>`

---

## 6) Setup - Main Flask App

## Prerequisites
- Python 3.10+ recommended
- MySQL-compatible database
- Cloudinary account

## Install

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
# source .venv/bin/activate

pip install -r requirements.txt
```



## Run

```bash
python run.py
```

Default dev URL: `http://127.0.0.1:5000`

---

## 7) Database Migrations

```bash
flask db init
flask db migrate -m "initial schema"
flask db upgrade
```

If your `FLASK_APP` is not set:

```bash
set FLASK_APP=run.py   # Windows (cmd)
# $env:FLASK_APP="run.py"   # PowerShell
```

---

## 8) Sentiment Service (Standalone)

The `Sentiment Analysis/` folder is an independent FastAPI service.

## Run Locally

```bash
cd "Sentiment Analysis"
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 7860 --reload
```

## API Endpoints
- `GET /health`
- `POST /predict`
- `POST /predict/batch`
- `GET /docs`

Current Flask integration calls a hosted endpoint:
- `https://priyam1105-sentiment-analysis-pro.hf.space/predict`

---

## 9) Recommendation Service Integration

The customer recommendation view calls:
- `https://priyam1105-vendor-recsys.hf.space/recommend`

Expected behavior:
1. Send `{ "customer_id": <int>, "top_n": 6 }`
2. Receive recommended vendor IDs
3. Query local `Vendor` records and render in ranked order

Local recommender experimentation files currently exist in:
- `Recommendation System/Copy_of_Untitled3.ipynb`
- `Recommendation System/synthetic_data_2026-03-26.csv`

---

## 10) Typical User Flow

1. User signs up and chooses role
2. User logs in and completes role profile
3. Customer browses vendors and books service
4. Vendor confirms and completes appointment
5. Customer submits rating + review
6. Review text is analyzed for sentiment and stored
7. Vendor sees sentiment mix in reviews dashboard
8. Customer requests personalized recommendations

---

## 11) Security and Production Notes

- Move hardcoded `SECRET_KEY` to environment variable
- Avoid committing `.env` files and credentials
- Add CSRF protection for form POST routes
- Add stricter ownership checks in some vendor service mutation routes
- Configure request retries/fallback for external ML API calls
- Consider rate limiting for auth and inference-triggering endpoints

---

## 12) Known Improvement Areas

- Add automated tests (unit + integration)
- Add service-level API contracts for recommender
- Add caching for recommendation/sentiment calls
- Containerize Flask app for environment consistency
- Add centralized logging and error monitoring

---

## 13) Quick Troubleshooting

- `ModuleNotFoundError`: confirm venv is activated and dependencies installed
- DB connection failures: verify `DB_PASSWORD` and DB host availability
- Image upload issues: verify Cloudinary credentials and network access
- Recommendation page empty: verify recommender endpoint response and local vendor IDs
- Sentiment fallback to neutral: API timeout/downstream errors default gracefully

---

## 14) License

No explicit project license file is currently present. Add a `LICENSE` file if distribution or open-source publication is planned.

