# Tradeoffs

Here are three things we deliberately *did not* build, and why. 

## 1. Full Authentication and SSO
**What we skipped:** We didn't implement JWTs, OAuth2, or a real login screen for the analysts. The API currently trusts the frontend.
**Why:** Implementing auth correctly (especially multi-tenant RBAC) takes a solid day. It proves we know how to use Django libraries, but it doesn't prove we know how to handle messy ESG data. For the prototype, we assume the user is an authenticated "Analyst" and focus our time on the ingestion and review workflows.

## 2. A Real Rules Engine for Validation
**What we skipped:** We hardcoded the validation rules (e.g., checking if the SAP `Werk` code is in a static Python dictionary `['W001', 'W002']`). We didn't build a dynamic rules engine where admins can configure validations per tenant.
**Why:** A dynamic rules engine requires complex UI and DB modeling (storing ASTs or JSON logic schemas). While necessary for production, a hardcoded lookup demonstrates the *concept* of the review queue (flagging bad data) perfectly. We traded configurability for speed.

## 3. Daily Proration of Utility Data
**What we skipped:** When a utility bill covers Jan 15 to Feb 14, we just assign the total carbon to Jan 15. We did not build the math to split the usage proportionally across January and February.
**Why:** Time-series proration in SQL is notoriously difficult. It requires calendar tables and complex joins to do efficiently at scale. Since the goal of the prototype is the *ingestion and review workflow*, getting bogged down in calendar math would have eaten half our timeline.

## Honest Assessment
This codebase is a solid foundation for the data model, but in a real production environment, the ingestion parsers (currently simple Python scripts) would need to be moved to an asynchronous task queue like Celery or AWS SQS. If a client uploads a 500MB SAP export, our current synchronous Django view will timeout.
