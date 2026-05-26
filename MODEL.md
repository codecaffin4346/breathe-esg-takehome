# Data Model

The hardest part of ESG ingestion isn't calculating `quantity * emission_factor`. It's knowing exactly *where* a number came from, *who* changed it, and *why*, six months after the fact when an auditor is looking at it.

Our data model is designed around three principles:
1. **Never mutate the raw payload:** We keep the exact JSON/CSV row we received.
2. **Track the lineage:** Every normalized emission record points back to its raw source.
3. **Multi-tenancy from day one:** You can't retrofit `tenant_id` into a B2B SaaS app later without a world of pain.

## Core Entities

### `Tenant`
The company we are onboarding (e.g., "Acme Corp"). 
- `id` (UUID, PK)
- `name` (String)

### `SourceSystem`
The system providing the data. This allows us to configure parsing rules per source.
- `id` (UUID, PK)
- `tenant_id` (FK -> Tenant)
- `name` (String) - e.g., "SAP S/4HANA US", "Concur EMEA", "PG&E Portal"
- `system_type` (Enum) - `SAP`, `UTILITY`, `TRAVEL`

### `RawDataRecord`
The immutable source of truth. When a CSV is uploaded or an API is pulled, we dump the exact row/object here. If our parser breaks, or an auditor asks for the source, this is the receipts.
- `id` (UUID, PK)
- `source_system_id` (FK -> SourceSystem)
- `raw_payload` (JSONB / JSON) - The exact key-value pairs from the source.
- `ingested_at` (DateTime)
- `status` (Enum) - `PENDING`, `PARSED`, `FAILED`

### `NormalizedEmission`
The canonical table our analysts interact with. Data gets parsed from `RawDataRecord` and mapped here.
- `id` (UUID, PK)
- `tenant_id` (FK -> Tenant)
- `raw_record_id` (FK -> RawDataRecord) - The lineage link.
- `scope` (Integer) - 1, 2, or 3.
- `category` (String) - e.g., "Purchased Goods", "Electricity", "Business Travel".
- `emission_date` (Date) - Normalized to a specific calendar day or start of a billing cycle.
- `quantity` (Float)
- `unit` (String) - e.g., "kWh", "liters", "km".
- `emission_factor` (Float) - The multiplier used (mocked in this prototype).
- `co2e` (Float) - The calculated carbon equivalent.
- `status` (Enum) - `PENDING_REVIEW`, `APPROVED`, `REJECTED`.
- `validation_errors` (JSON) - e.g., `["Unknown Plant Code: Werk1"]`. This is what drives the UI error states.

### `AuditLog`
We track every manual intervention. If an analyst fixes a plant code, we log it.
- `id` (UUID, PK)
- `record_id` (FK -> NormalizedEmission)
- `action` (Enum) - `EDITED`, `APPROVED`, `REJECTED`
- `user` (String) - Mocked to "Analyst" for the prototype.
- `previous_state` (JSON) - What the row looked like before.
- `new_state` (JSON) - What the row looks like after.
- `timestamp` (DateTime)

## Why This Shape?

This schema acknowledges that ETL in sustainability is messy. By separating `RawDataRecord` from `NormalizedEmission`, we can safely blow away and re-parse the normalized data if we realize we mapped a German SAP header incorrectly, without losing the original client data dump.
