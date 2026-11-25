import json
from experiments.benchmark import run_benchmark


def main() -> None:
    summary = run_benchmark()
    for rec in summary.get("scenarios", []):
        print(
            rec["scenario"],
            "| acc_rate:", rec["accepted_rate"],
            "| avg_attempts:", rec["avg_attempts"],
            "| states:", rec["final_states"],
            "| avg_ms:", rec["avg_latency_ms"],
        )
    print("Verdicts:", json.dumps(summary["verdicts"], ensure_ascii=False))
    print("Fingerprint:", summary["fingerprint"])


if __name__ == "__main__":
    main()