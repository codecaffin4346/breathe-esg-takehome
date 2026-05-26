# Decisions

A 4-day prototype forces ruthless scoping. Here is exactly what we chose to build, the ambiguities we resolved, and what we'd ask the PM.

## 1. SAP Data: Handling the ALV Grid Reality
**Decision:** We assume SAP data arrives as a flat CSV export (typical of an ALV grid dump or IDoc flat file), not a clean OData JSON payload.
**Why:** While modern S/4HANA supports OData, many enterprise clients are still running ECC6 or custom on-prem instances. The lowest common denominator for pulling procurement data without IT fighting you for 6 months is a scheduled CSV export. 
**Subset Handled:** We handle a standard procurement dump with German headers (`Menge` for quantity, `MEins` for unit, `Werk` for plant) and inconsistent date strings (`DD.MM.YYYY`). We explicitly drop lines with zero quantity, assuming them to be cancelled POs.

## 2. Utility Data: The Portal Scrape
**Decision:** We assume the utility data is a CSV downloaded from a portal (e.g., following the Green Button "Download My Data" CSV shape), rather than PDF bills.
**Why:** OCR'ing PDF bills is a distraction for a core workflow prototype. It's an entire product on its own. A portal CSV is realistic for a facilities team managing multiple sites.
**Subset Handled:** We handle the "Billing Period" problem. Utility bills rarely align to a calendar month (e.g., Jan 14 - Feb 12). For this prototype, we map the emission date to the *start date* of the billing period. 

## 3. Travel Data: The API Pull
**Decision:** We simulate an API pull from a modern travel platform (like Navan or Concur via Thrust Carbon). We accept JSON payloads.
**Why:** Unlike SAP or local utilities, travel platforms are SaaS-native and have good REST APIs. 
**Subset Handled:** We handle Flight itineraries. We handle the edge case where the API gives us `origin` and `destination` airport codes (e.g., SFO -> LHR) but *not* the distance. We use a mock lookup to calculate distance if missing.

## Ambiguities Resolved
*   **"Let our analysts review and sign off"**: What does sign off mean? 
    *   *Resolution:* It means transitioning a row from `PENDING_REVIEW` to `APPROVED`. Once approved, it is locked (read-only) and an AuditLog entry is generated.
*   **"What failed, what looks suspicious"**: How do we define suspicious?
    *   *Resolution:* We run a basic validation pass upon ingestion. If a plant code isn't in our known lookup table, or if a quantity is extremely high (> 1,000,000), we flag it in a `validation_errors` JSON field. The React UI highlights these rows in red/yellow.

## Questions for the PM
1.  **Unit Normalization:** When an SAP export gives us `ST` (Stück / Pieces) instead of `kg` or `liters`, who is responsible for the conversion factor? Do we build a global conversion table, or is that mapped per-tenant?
2.  **Proration:** For utility bills spanning months, do auditors accept assigning the whole emission to the start month, or do they mandate prorating it daily across both months?
3.  **Source Updates:** If a client re-uploads a CSV with corrected SAP data for the same month, do we overwrite the existing `RawDataRecord` or version it?
