# User Guide — Vireo Autonomous Agent Network

## 1. What Vireo Autonomous Agent Network Is

**Vireo** is an open coordination and control plane (`Coordination & Control Plane`) for autonomous AI agents built on top of **A2A** (agent discovery and interaction via signed `Agent Card` metadata) and **MCP** (tools and data). Every task run goes through a commitment contract, **Ed25519** cryptographic signature verification, dynamic target agent assignment, and JSON schema validation for outputs.

## 2. Who It Is For

- **Autonomous AI agent and multi-agent system developers** who need governed control, cryptographic agent cards, explicit agent assignment, and execution contracts.
- **AI engineers and reliability/security researchers** testing agent behavior under data tampering, invalid JSON schemas, cancellations, custom security roles, and retries.
- **Teams building local, privacy-first solutions** requiring dynamic identity generation (`did:vireo:...`) and local contract execution.
- **Architects and tech leads** looking for a tangible demonstration of how A2A discovery and contract enforcement ensure reliability.

## 3. Key Capabilities

- **Task Contract State Machine:** deterministic flow `DISCOVER → PROPOSE → NEGOTIATE → COMMIT → EXECUTE → VERIFY → DONE` with exception transitions:
  - cancellation `PROPOSE / NEGOTIATE / COMMIT / EXECUTE → CANCELLED`;
  - return to negotiation `NEGOTIATE → PROPOSE`;
  - retries `VERIFY → EXECUTE` (up to 2 retries) or failure termination `VERIFY → FAILED`.
- **Dynamic Agent Identity & Registration:**
  - Create signed `Agent Card` instances directly in the Streamlit UI.
  - Automatically generate **Ed25519** keypairs and DID identifiers (`did:vireo:...`).
  - Store registered identities in `results/registered_agents.json`.
- **Targeted Agent Assignment & A2A Discovery:**
  - Filter active agents by capability in the sidebar (e.g., `security_audit`, `metrics_reader`).
  - Explicitly select a target agent for task execution via **Target / Assigned Agent (A2A)** dropdown.
- **Trust & Data Integrity:** cryptographic verification, output artifact hashing, and schema enforcement.

## 4. Control Web UI Structure

- **Left Sidebar (`Vireo Control Plane`):**
  - Active protocol indicators (*Ed25519 Signed DIDs*, *Contract Machine States*, *JSON Schema + Artifact Hash*).
  - **A2A Discovery:** capability search filter and verified agent list showing assigned `did:vireo:...` identifiers.
  - **Run Full System Benchmark** button.
- **Main Workspace:**
  - **Submit & Verify Task Tab:**
    - **Target / Assigned Agent (A2A)** selector.
    - `Task Objective` input field.
    - Scenario toggles (`Honest Agent Execution`, `Enable Vireo Verification`, `Simulate Bad Schema`, `Simulate Cancel`).
    - **Execute Contract Task** action button and execution state display (`Final Contract State: DONE / CANCELLED / FAILED`).
  - **Register Task Agent Tab:**
    - Form to create new agents (`Agent Name / Role`, `Capabilities`, `Agent Endpoint`).
    - **Register Agent** button to sign the card and append it to the registry.
- **Right Panel (`Latest Benchmark History`):** benchmark protocol info, reproducibility fingerprint (`baad76ec2455`), verdict checklist, and execution summary.

## 5. How to Use It (Windows)

### Step 1. Run Unit Tests and Multi-Iteration Benchmark
Run `.\run_vireo.bat` in the terminal.

### Step 2. Launch Control Web UI
Run `.\run_ui.bat` in the terminal and open `http://localhost:8501` in your browser.

### Step 3. Register a Custom Agent
1. Navigate to the **Register Task Agent** tab.
2. Enter the role (e.g., `security_auditor`), comma-separated capabilities (e.g., `security_audit, schema_audit, integrity_check`), and endpoint.
3. Click **Register Agent** to generate its `did:vireo:...` identity.

### Step 4. Submit & Verify Task
1. Switch to **Submit & Verify Task**.
2. Select your newly registered agent in **Target / Assigned Agent (A2A)**.
3. Enter your task prompt in `Task Objective`.
4. Choose execution toggles and click **Execute Contract Task**.