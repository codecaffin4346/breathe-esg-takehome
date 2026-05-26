# Breathe ESG Data Ingestion Prototype

A full-stack Django and React prototype designed to ingest, normalize, and audit messy emissions data from SAP, Utility portals, and Corporate Travel platforms.

## Live Deployment
**👉 [Live Dashboard](https://breathe-esg-takehome-production.up.railway.app/)**

*Note: The application is deployed on Railway using a Docker container. Because it uses an ephemeral SQLite database for this prototype, any data you edit/approve will reset to the original mock state if the server goes to sleep and spins back up.*

## Assignment Deliverables

The PM explicitly requested four core design documents. Please review them in the following order:

1. [**MODEL.md**](./MODEL.md): Explains the data schema. Focuses on the separation between `RawDataRecord` (immutable source of truth) and `NormalizedEmission`, ensuring deep auditability.
2. [**SOURCES.md**](./SOURCES.md): Details the research behind the mock data. Shows how we handle German SAP headers, misaligned utility billing periods, and missing travel API distances.
3. [**DECISIONS.md**](./DECISIONS.md): Details the ambiguities resolved during the 4-day prototype window, including how we scoped down the SAP CSV format and handled utility proration.
4. [**TRADEOFFS.md**](./TRADEOFFS.md): Highlights three specific things deliberately omitted (SSO/Auth, dynamic rules engine, complex time-series SQL) and why they are distractions for this stage.

## How it works

### The Analyst UX
If you visit the live URL, you will see the Analyst Review Queue. 
- The system automatically parses the raw mock data and flags suspicious rows (e.g., an SAP entry with an "Unknown Plant Code: W999", or a missing travel distance). 
- Flagged rows are highlighted in red for review. 
- Valid rows can be clicked to **Approve**. Once approved, they are locked, and an immutable entry is added to the `AuditLog` table.

### Local Development

If you wish to run the monolithic repository locally:

```bash
# 1. Install Python backend dependencies
pip install -r backend/requirements.txt

# 2. Install Node frontend dependencies
cd frontend && npm install && npm run build && cd ..

# 3. Setup the database and load realistic mock data
python manage.py migrate
python manage.py load_mock_data

# 4. Start the server (serves the React frontend via Django)
python manage.py runserver
```
Navigate to `http://127.0.0.1:8000/`.
