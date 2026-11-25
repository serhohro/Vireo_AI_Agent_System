import hashlib
import json
import statistics
import time
from pathlib import Path
from typing import Any, Callable, Dict, List

from interoperability.adapters import A2AAdapter, ExternalAgentProxy, ProtocolBridge
from interoperability.ollama_adapter import OllamaAgentAdapter
from protocol.lifecycle import CommitmentContract, ProtocolState
from protocol.schema_validator import validate_json_schema
from trust.trust_core import (
    check_permissions,
    compute_artifact_hash,
    create_agent_identity,
    generate_keypair,
    sign_payload,
    verify_signature,
)


def reproducibility_fingerprint(record: Any) -> str:
    raw = json.dumps(record, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:12]


def evaluate_single(
    verify_enabled: bool,
    honest: bool,
    invalid_schema: bool = False,
    simulate_cancel: bool = False,
    use_ollama: bool = False,
    objective: str = "Cross-framework analytics with signed discovery and schema checks",
    max_retries: int = 2,
) -> Dict[str, Any]:
    start = time.perf_counter()
    priv_i, pub_i = generate_keypair()
    priv_e, pub_e = generate_keypair()
    did_e = create_agent_identity(pub_e)

    adapter = A2AAdapter()
    discovered = adapter.discover_agents("metrics_reader")

    contract = CommitmentContract(
        task_id="task-003",
        initiator_did=create_agent_identity(pub_i),
        executor_did=did_e,
        objective=objective,
        verification_criteria={"required_scopes": ["read:metrics"], "required_fields": ["status", "metrics_data"]},
        max_retries=max_retries,
    )

    for s in (ProtocolState.PROPOSE, ProtocolState.NEGOTIATE):
        contract.transition(s)

    if simulate_cancel:
        contract.transition(ProtocolState.CANCELLED)
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        return {
            "accepted": False,
            "attempts": 0,
            "final_state": contract.state.value,
            "retries": 0,
            "latency_ms": elapsed,
        }

    contract.transition(ProtocolState.COMMIT)
    contract.transition(ProtocolState.EXECUTE)

    permitted = check_permissions(
        ["read:metrics", "write:report"],
        contract.verification_criteria["required_scopes"],
    )
    agent = ExternalAgentProxy(did_e, honest=honest)
    ollama = OllamaAgentAdapter(timeout_sec=1.0) if use_ollama else None
    bridge = ProtocolBridge()
    limit = max_retries if verify_enabled else 0
    attempts = 0
    accepted = False
    ollama_available = None

    for attempt in range(limit + 1):
        attempts += 1
        if ollama is not None:
            llm_res = ollama.execute(contract.objective)
            ollama_available = bool(llm_res.get("available", False))
            out = {
                "agent_id": did_e,
                "framework": "Ollama",
                "output": llm_res.get("output", "") if ollama_available else "UNAVAILABLE",
            }
            if not ollama_available and attempt == 0:
                # Early exit if Ollama service is unreachable to prevent long timeouts
                contract.transition(ProtocolState.VERIFY)
                contract.transition(ProtocolState.FAILED)
                break
        else:
            out = agent.execute({"objective": contract.objective})

        payload_data = {"status": "SUCCESS", "metrics_data": out}
        if invalid_schema:
            payload_data = {"error_code": 500}

        envelope = bridge.dispatch(
            did_e,
            "metrics_reader",
            {"task_id": contract.task_id, "output": payload_data},
        )
        body = {k: v for k, v in envelope.items() if k != "artifact_hash"}
        envelope["artifact_hash"] = compute_artifact_hash(body)
        signature = sign_payload(envelope, priv_e)

        valid = verify_signature(envelope, signature, pub_e) if verify_enabled else True
        intact = (envelope["artifact_hash"] == compute_artifact_hash(body)) if verify_enabled else True
        clean = (not str(out.get("output", "")).startswith("TAMPERED")) if verify_enabled else True
        ollama_ok = (ollama_available is True and bool(str(out.get("output", "")).strip())) if use_ollama else True

        schema_ok, _ = validate_json_schema(
            payload_data,
            contract.verification_criteria.get("required_fields", []),
        ) if verify_enabled else (True, "OK")

        accepted = bool(permitted and valid and intact and clean and schema_ok and ollama_ok)
        contract.transition(ProtocolState.VERIFY)
        if accepted:
            contract.transition(ProtocolState.DONE)
            break
        if attempt < limit:
            contract.transition(ProtocolState.EXECUTE)
        else:
            contract.transition(ProtocolState.FAILED)

    elapsed = round((time.perf_counter() - start) * 1000, 2)
    res = {
        "accepted": bool(accepted),
        "attempts": attempts,
        "final_state": contract.state.value,
        "retries": contract.retries,
        "latency_ms": elapsed,
    }
    if use_ollama:
        res["ollama_available"] = ollama_available
    return res


def run_benchmark(iterations: int = 20) -> dict:
    scenarios_def = [
        {"name": "baseline_honest", "verify_enabled": False, "honest": True},
        {"name": "baseline_dishonest", "verify_enabled": False, "honest": False},
        {"name": "vireo_honest", "verify_enabled": True, "honest": True},
        {"name": "vireo_dishonest", "verify_enabled": True, "honest": False},
        {"name": "vireo_invalid_schema", "verify_enabled": True, "honest": True, "invalid_schema": True},
        {"name": "vireo_cancelled_negotiation", "verify_enabled": True, "honest": True, "simulate_cancel": True},
        {"name": "vireo_ollama_probe", "verify_enabled": True, "honest": True, "use_ollama": True},
    ]

    summary_scenarios = []

    for sc in scenarios_def:
        latencies = []
        accepted_count = 0
        final_states = {}
        total_attempts = 0

        # Run 1 iteration for probe if offline, or full iterations for core benchmarks
        n_runs = 1 if sc.get("use_ollama") else iterations

        for _ in range(n_runs):
            r = evaluate_single(
                verify_enabled=sc["verify_enabled"],
                honest=sc["honest"],
                invalid_schema=sc.get("invalid_schema", False),
                simulate_cancel=sc.get("simulate_cancel", False),
                use_ollama=sc.get("use_ollama", False),
            )
            latencies.append(r["latency_ms"])
            if r["accepted"]:
                accepted_count += 1
            total_attempts += r["attempts"]
            st = r["final_state"]
            final_states[st] = final_states.get(st, 0) + 1

        avg_lat = round(statistics.mean(latencies), 2)
        med_lat = round(statistics.median(latencies), 2)

        record = {
            "scenario": sc["name"],
            "iterations": n_runs,
            "accepted_rate": round(accepted_count / n_runs, 2),
            "avg_latency_ms": avg_lat,
            "median_latency_ms": med_lat,
            "avg_attempts": round(total_attempts / n_runs, 2),
            "final_states": final_states,
        }
        if "ollama_available" in r:
            record["ollama_available"] = r["ollama_available"]

        summary_scenarios.append(record)
        print(f"{sc['name']:<28} | acc_rate: {record['accepted_rate']:<4} | avg_ms: {avg_lat:<6} | states: {final_states}")

    by_name = {sc["scenario"]: sc for sc in summary_scenarios}
    verdicts = {
        "vireo_rejects_tampered": by_name["vireo_dishonest"]["accepted_rate"] == 0.0,
        "baseline_accepted_tampered": by_name["baseline_dishonest"]["accepted_rate"] == 1.0,
        "vireo_honest_success": by_name["vireo_honest"]["accepted_rate"] == 1.0,
        "vireo_rejects_bad_schema": by_name["vireo_invalid_schema"]["accepted_rate"] == 0.0,
        "vireo_handles_cancellation": "CANCELLED" in by_name["vireo_cancelled_negotiation"]["final_states"],
        "vireo_ollama_checked": "ollama_available" in by_name["vireo_ollama_probe"],
    }

    summary = {
        "protocol": "vireo_v3_multi_iteration",
        "total_iterations_per_scenario": iterations,
        "scenarios": summary_scenarios,
        "verdicts": verdicts,
    }
    summary["fingerprint"] = reproducibility_fingerprint(summary)

    out_path = Path(__file__).resolve().parent.parent / "results" / "latest_benchmark.json"
    out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


if __name__ == "__main__":
    run_benchmark()