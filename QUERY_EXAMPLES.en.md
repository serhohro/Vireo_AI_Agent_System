# Query Examples for Vireo Control Panel (`Task Objective`)

This file provides ready-to-use prompt examples for the **`Task Objective`** field in the **Vireo** web UI (`http://localhost:8501`) incorporating explicit **Target / Assigned Agent (A2A)** selection and scenario toggles.

## 1. Honest Execution with Assigned Agent (`Honest Execution`)

Suitable for testing the full `DISCOVER → PROPOSE → NEGOTIATE → COMMIT → EXECUTE → VERIFY → DONE` flow using a designated target agent:

- **Target / Assigned Agent:** `planner` or `security_auditor`
- **Prompt / Objective:** `Calculate cross-framework analytics and verify schema compliance`
- **Settings:** `Honest Agent Execution` — enabled; `Enable Vireo Verification` — enabled; `Simulate Bad Schema` — disabled; `Simulate Cancel` — disabled.

## 2. Security Audit & Integrity Check (`Security Auditor Role`)

Suitable for executing auditing tasks directly through a dynamically registered `security_auditor`:

- **Target / Assigned Agent:** `security_auditor (security_audit, schema_audit, integrity_check)`
- **Prompt / Objective:** `Audit payload signatures, verify Ed25519 attestation, and compute artifact hash`
- **Settings:** `Honest Agent Execution` — enabled; `Enable Vireo Verification` — enabled; `Simulate Bad Schema` — disabled; `Simulate Cancel` — disabled.

## 3. Dishonest Agent / Tampered Output (`Dishonest Agent`)

Suitable for comparing unverified execution against Vireo enforcement (`vireo_rejects_tampered` / retries and `FAILED` state):

- **Target / Assigned Agent:** Any registered agent
- **Prompt / Objective:** `Generate financial summary report with signed agent attestation`
- **Settings for Vireo Verification:** `Honest Agent Execution` — disabled; `Enable Vireo Verification` — enabled; `Simulate Bad Schema` — disabled; `Simulate Cancel` — disabled.

## 4. JSON Schema Violation (`Simulate Bad Schema`)

Suitable for verifying output schema enforcement and handling failed retries:

- **Target / Assigned Agent:** Any registered agent
- **Prompt / Objective:** `Produce structured JSON payload matching target schema for downstream MCP tool`
- **Settings:** `Honest Agent Execution` — enabled or disabled; `Enable Vireo Verification` — enabled; `Simulate Bad Schema` — enabled; `Simulate Cancel` — disabled.

## 5. Task Cancellation (`Simulate Cancel`)

Suitable for confirming immediate state transitions into `CANCELLED` prior to execution attempts (`attempts: 0`):

- **Target / Assigned Agent:** Any registered agent
- **Prompt / Objective:** `Coordinate multi-step data pipeline across discovered A2A agents`
- **Settings:** `Honest Agent Execution` — enabled; `Enable Vireo Verification` — enabled; `Simulate Bad Schema` — disabled; `Simulate Cancel` — enabled.