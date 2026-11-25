# Vireo Autonomous Agent Network

An innovative open coordination and control plane (`Coordination & Control Plane`) for autonomous AI agents built on top of **A2A** (agent discovery and interaction via signed `Agent Card` metadata with `did:vireo:...` identities and Ed25519 keypairs) and **MCP** (tools and data).

Built around a custom W3C-registered decentralized identifier method **`did:vireo`**, the project tackles a core challenge of autonomous multi-agent systems: **trust, cryptographic accountability, and result integrity verification** rather than blind execution. Every task run passes through a commitment contract, cryptographic signature verification, dynamic agent assignment, and JSON schema validation.

[Українська версія](./README.uk.md) · [Releases](https://github.com/serhohro/Vireo_AI_Agent_System/releases) · [vireo-ai-communicator-api](https://github.com/serhohro/vireo-ai-communicator-api)

## Key Capabilities

- **Custom `did:vireo` Identity & Ed25519 Signatures:** each agent uses an Ed25519 key pair, a signed `Agent Card`, and a `did:vireo:...` identifier to verify origin and action accountability.
- **Task Contract State Machine:** deterministic flow `DISCOVER -> PROPOSE -> NEGOTIATE -> COMMIT -> EXECUTE -> VERIFY -> DONE` with support for exceptions:
  - cancellation `PROPOSE / NEGOTIATE / COMMIT / EXECUTE -> CANCELLED`;
  - return to negotiation `NEGOTIATE -> PROPOSE`;
  - retries `VERIFY -> EXECUTE` (up to 2 retries) or failure termination `VERIFY -> FAILED`.
- **Dynamic Agent Identity & Discovery:**
  - On-the-fly registration of signed `Agent Card` objects with custom capabilities (e.g., `security_auditor` with `security_audit, schema_audit, integrity_check`).
  - Cryptographic keypair generation (**Ed25519**) and custom DID minting (`did:vireo:...`).
  - Persistent registry management stored locally (`results/registered_agents.json`).
  - Real-time A2A agent filtering and targeted agent assignment in UI tasks.
- **Trust & Data Integrity:** cryptographic agent validation, payload artifact hashing, and output JSON schema enforcement.
- **Local Autonomy & Privacy:** tests, benchmarks, and agent registrations run locally without external data transfer.
- **Control Web UI (`Streamlit`):**
  - **Submit & Verify Task:** assign target agents, submit custom `Task Objective` prompts, toggle honest/dishonest execution, invalid schema, or cancellation.
  - **Register Task Agent:** mint signed custom agent identity cards on the fly.
  - Inspect system metrics and benchmark history at `http://localhost:8501`.

## Benchmark Results (`vireo_v3_multi_iteration`)

Latest recorded reproducibility `Fingerprint`: **`c72b85dcb98b`** (`results/latest_benchmark.json`).

| Scenario | Iterations | `accepted_rate` | Avg. Attempts | Final States | Avg. Latency |
| :--- | :---: | :---: | :---: | :--- | :---: |
| `baseline_honest` | 20 | `1.0` | `1.0` | `{'DONE': 20}` | `1.01 ms` |
| `baseline_dishonest` | 20 | `1.0` | `1.0` | `{'DONE': 20}` | `1.05 ms` |
| `vireo_honest` | 20 | `1.0` | `1.0` | `{'DONE': 20}` | `1.16 ms` |
| `vireo_dishonest` | 20 | `0.0` | `3.0` | `{'FAILED': 20}` | `1.6 ms` |
| `vireo_invalid_schema` | 20 | `0.0` | `3.0` | `{'FAILED': 20}` | `1.17 ms` |
| `vireo_cancelled_negotiation` | 20 | `0.0` | `0.0` | `{'CANCELLED': 20}` | `0.47 ms` |
| `vireo_ollama_probe` | 1 | `0.0` | `1.0` | `{'FAILED': 1}` | `1039.96 ms` |

**Verified Verdicts:**
- `vireo_rejects_tampered`: `true`
- `baseline_accepted_tampered`: `true`
- `vireo_honest_success`: `true`
- `vireo_rejects_bad_schema`: `true`
- `vireo_handles_cancellation`: `true`
- `vireo_ollama_checked`: `true`

## Quick Start (Windows)

1. Run `setup_vireo_project.bat` for initial environment setup (if needed).
2. Run unit tests and the multi-iteration benchmark (`results\latest_benchmark.json`):
   ```bat
   .\run_vireo.bat
