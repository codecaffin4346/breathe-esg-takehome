# Breathe ESG — Data Ingestion Prototype

A full-stack prototype that ingests emissions and activity data from three real-world enterprise sources — SAP (fuel/procurement), utility portals (electricity), and a corporate travel platform (Navan/Concur) — normalizes it, and surfaces a review dashboard where analysts can flag, inspect, and approve records before they go to auditors.

Built in 4 days with Django REST Framework and React (Vite + TypeScript).

## Live URL

**👉 https://breathe-esg-takehome-production.up.railway.app/**

> This prototype uses SQLite. Because Railway's filesystem is ephemeral, approved/rejected rows will reset to their original mock state if the container restarts. In a production system, this would be replaced with a persistent Postgres database.

---

## Required Documents

These carry most of the evaluation weight. Please read them in order.

| Document | What it covers |
|---|---|
| [MODEL.md](./MODEL.md) | Full data schema, multi-tenancy, source-of-truth design, audit trail |
| [SOURCES.md](./SOURCES.md) | Research on real-world SAP, utility, and travel data formats. Why the mock data looks the way it does |
| [DECISIONS.md](./DECISIONS.md) | Every ambiguity resolved, what was chosen, and what we'd ask the PM |
| [TRADEOFFS.md](./TRADEOFFS.md) | Three things deliberately not built and exactly why |

---

## What the app does

### Ingestion

Three data sources are parsed on startup via a Django management command (`load_mock_data`):

| Source | Format | File |
|---|---|---|
| SAP ECC6 (Fuel/Procurement) | CSV with German headers (`Werk`, `Menge`, `MEins`), `DD.MM.YYYY` dates | `data/sap_export.csv` |
| PG&E Utility Portal | Green Button-style CSV with misaligned billing periods | `data/utility_export.csv` |
| Navan Travel API | JSON payload with missing flight distances requiring fallback lookup | `data/travel_api.json` |

Each raw row is stored verbatim in `RawDataRecord` (immutable) before being parsed into `NormalizedEmission`. This means the original client data is never modified.

### Validation & Flagging

During parsing, rows are checked against basic rules:
- SAP rows with plant codes not in the known lookup (`W001`, `W002`) are flagged as **"Unknown Plant Code"**
- SAP rows with quantities above 100,000 are flagged as **"Suspiciously high quantity"**
- Travel rows where distance is missing trigger a **fallback lookup** (e.g. SFO → LHR = 8,600km) and are flagged with a warning

Flagged rows show up highlighted in red in the dashboard.

### Analyst Review Queue

The React dashboard at the root URL shows all ingested records. Analysts can:
- See validation warnings inline on flagged rows
- Click **Approve** to lock a clean record — this writes an immutable entry to the `AuditLog` table with a timestamp and the previous/new state
- Approved records are locked (read-only)

### API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/emissions/` | GET | List all normalized emission records |
| `/api/emissions/{id}/approve/` | POST | Approve a record and write to audit log |
| `/api/audits/` | GET | List all audit log entries |

---

## Running Locally

```bash
# 1. Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\activate   # Windows
source venv/bin/activate  # Mac/Linux

# 2. Install Python dependencies
pip install -r backend/requirements.txt

# 3. Build the React frontend
cd frontend
npm install
npm run build
cd ..

# 4. Run migrations and load mock data
python manage.py migrate
python manage.py load_mock_data

# 5. Start the server
python manage.py runserver
```

Navigate to `http://127.0.0.1:8000/`

---

## Project Structure

```
breathe_esg/
├── backend/            # Django settings, urls, wsgi
├── ingest/             # Django app — models, views, serializers, parsers
│   └── management/
│       └── commands/
│           └── load_mock_data.py   # The ingestion engine
├── data/               # Realistic mock data files
│   ├── sap_export.csv
│   ├── utility_export.csv
│   └── travel_api.json
├── frontend/           # React + Vite + TypeScript
│   └── src/App.tsx     # Analyst review dashboard
├── MODEL.md
├── SOURCES.md
├── DECISIONS.md
├── TRADEOFFS.md
├── Dockerfile
└── build.sh
```

---

## Tech Stack

- **Backend**: Python 3.11, Django 5, Django REST Framework
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS
- **Database**: SQLite (prototype) — swap `DATABASE_URL` for Postgres in production
- **Deployment**: Docker on Railway
