import json
from pathlib import Path
import streamlit as st

from experiments.benchmark import evaluate_single, run_benchmark
from interoperability.adapters import A2AAdapter

st.set_page_config(
    page_title="Vireo Autonomous Agent Network",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .status-badge { padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 0.85rem; display: inline-block; }
    .status-done { background-color: #238636; color: #ffffff; }
    .status-failed { background-color: #da3633; color: #ffffff; }
    .status-cancelled { background-color: #6e7681; color: #ffffff; }
    </style>
    """,
    unsafe_allow_html=True,
)

store_path = Path(__file__).resolve().parent.parent / "results" / "registered_agents.json"
adapter = A2AAdapter(card_store_path=store_path)

with st.sidebar:
    st.title("⚡ Vireo Control Plane")
    st.caption("A2A & MCP Autonomous Agent Coordination Framework")
    st.divider()

    st.subheader("🛠️ Active Protocols")
    st.markdown("- **Trust Engine**: Ed25519 Signed DIDs")
    st.markdown("- **Lifecycle**: Contract Machine States")
    st.markdown("- **Integrity**: JSON Schema + Artifact Hash")
    st.divider()

    st.subheader("📡 A2A Discovery")
    capability_filter = st.text_input("Capability Filter", value="metrics_reader")
    agents = adapter.discover_agents(capability_filter.strip())
    all_agents = adapter.list_all_agents()
    st.write(f"Verified Agents Found: `{len(agents)}` (Total: `{len(all_agents)}`)")
    for a in agents:
        caps = ", ".join(a.get("capabilities", []))
        st.caption(f"• **{a.get('name')}** (`{str(a.get('did', ''))[:18]}...`) — *{caps}*")

    st.divider()
    if st.button("🔄 Run Full System Benchmark", type="primary"):
        with st.spinner("Running 20-iteration benchmark..."):
            res = run_benchmark(iterations=20)
            st.success(f"Benchmark Complete! Fingerprint: `{res['fingerprint']}`")

st.title("⚡ AI Task Agent Control Panel")
st.caption("Submit tasks — the Vireo engine enforces commitment contracts, cryptographic signatures, and schema validation.")

col_main, col_history = st.columns([2, 1])

with col_main:
    tab_task, tab_register = st.tabs(["📝 Submit & Verify Task", "➕ Register Task Agent"])

    with tab_task:
        selected_agent = None
        if all_agents:
            agent_labels = [
                f"{a.get('name')} ({', '.join(a.get('capabilities', []))}) — {str(a.get('did', ''))[:18]}..."
                for a in all_agents
            ]
            chosen_idx = st.selectbox(
                "Target / Assigned Agent (A2A)",
                options=list(range(len(all_agents))),
                format_func=lambda i: agent_labels[i],
            )
            selected_agent = all_agents[chosen_idx]

        with st.form("task_form"):
            objective = st.text_area(
                "Task Objective",
                value="Calculate cross-framework analytics and verify schema compliance",
                height=100,
            )
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                honest_mode = st.checkbox("Honest Agent Execution", value=True)
            with c2:
                verify_mode = st.checkbox("Enable Vireo Verification", value=True)
            with c3:
                bad_schema = st.checkbox("Simulate Bad Schema", value=False)
            with c4:
                cancel_mode = st.checkbox("Simulate Cancel", value=False)

            submitted = st.form_submit_button("▶ Execute Contract Task")

        if submitted:
            st.subheader("📊 Execution Flow & Result")
            effective_objective = objective.strip() or "Default contract objective"
            if selected_agent is not None:
                effective_objective = (
                    f"[Agent: {selected_agent.get('name')} | DID: {selected_agent.get('did')}] "
                    f"{effective_objective}"
                )

            with st.spinner("Executing task lifecycle..."):
                res = evaluate_single(
                    verify_enabled=verify_mode,
                    honest=honest_mode,
                    invalid_schema=bad_schema,
                    simulate_cancel=cancel_mode,
                    objective=effective_objective,
                )

            state_val = res["final_state"]
            if state_val == "DONE":
                st_class = "status-done"
            elif state_val == "CANCELLED":
                st_class = "status-cancelled"
            else:
                st_class = "status-failed"

            st.markdown(
                f"**Final Contract State:** <span class='status-badge {st_class}'>{state_val}</span>",
                unsafe_allow_html=True,
            )

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Accepted", str(res["accepted"]))
            m2.metric("Attempts Used", res["attempts"])
            m3.metric("Retries Count", res["retries"])
            m4.metric("Latency (ms)", res["latency_ms"])

            st.json(res)

    with tab_register:
        st.markdown("Create a signed `Agent Card` with a new `did:vireo:...` identity and Ed25519 keypair.")
        with st.form("register_agent_form"):
            agent_name = st.text_input("Agent Name / Role", placeholder="metrics_auditor")
            capabilities_raw = st.text_input(
                "Capabilities (comma-separated)",
                value="metrics_reader, schema_audit",
            )
            endpoint_url = st.text_input(
                "Agent Endpoint",
                value="local://vireo/metrics_auditor",
            )
            reg_submitted = st.form_submit_button("🔐 Register Agent")

        if reg_submitted:
            caps = [c.strip() for c in capabilities_raw.split(",") if c.strip()]
            try:
                created_card = adapter.register_agent(
                    name=agent_name,
                    capabilities=caps,
                    endpoint=endpoint_url,
                )
                st.success(f"Registered agent `{created_card['name']}` with DID `{created_card['did']}`")
                st.json(created_card)
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))

with col_history:
    st.subheader("⏱️ Latest Benchmark History")
    json_path = Path(__file__).resolve().parent.parent / "results" / "latest_benchmark.json"

    if json_path.exists():
        bench_data = json.loads(json_path.read_text(encoding="utf-8"))
        st.caption(f"Protocol: `{bench_data.get('protocol')}`")
        st.caption(f"Fingerprint: `{bench_data.get('fingerprint')}`")

        st.divider()
        st.markdown("**Verdicts:**")
        for k, v in bench_data.get("verdicts", {}).items():
            st.markdown(f"- `{k}`: {'✅' if v else '❌'}")

        st.divider()
        st.markdown("**Scenario Summary:**")
        for sc in bench_data.get("scenarios", []):
            st.markdown(f"**{sc['scenario']}**")
            st.caption(
                f"Runs: `{sc.get('iterations', 1)}` | Acc: `{sc['accepted_rate']}` | "
                f"Avg: `{sc['avg_latency_ms']} ms` | Med: `{sc.get('median_latency_ms', sc['avg_latency_ms'])} ms`"
            )
    else:
        st.info("No benchmark results found. Click 'Run Full System Benchmark' in the sidebar.")
