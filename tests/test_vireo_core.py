import pytest
from interoperability.adapters import A2AAdapter, build_signed_agent_card, verify_agent_card
from protocol.lifecycle import CommitmentContract, ProtocolState
from protocol.schema_validator import validate_json_schema
from trust.trust_core import create_agent_identity, generate_keypair, sign_payload, verify_signature


def test_ed25519_sign_and_verify():
    priv, pub = generate_keypair()
    did = create_agent_identity(pub)
    assert did.startswith("did:vireo:")
    payload = {"task": "t1", "value": 42}
    sig = sign_payload(payload, priv)
    assert verify_signature(payload, sig, pub) is True
    assert verify_signature({"task": "t1", "value": 99}, sig, pub) is False


def test_signed_agent_card_discovery():
    card = build_signed_agent_card("worker", ["metrics_reader"])
    assert verify_agent_card(card) is True
    tampered = dict(card)
    tampered["card"] = dict(card["card"])
    tampered["card"]["name"] = "forged"
    assert verify_agent_card(tampered) is False

    adapter = A2AAdapter()
    found = adapter.discover_agents("metrics_reader")
    assert len(found) >= 1


def test_lifecycle_retries_and_limits():
    c = CommitmentContract(
        task_id="t-life",
        initiator_did="did:vireo:init",
        executor_did="did:vireo:exec",
        objective="test",
        max_retries=2,
    )
    for st in (
        ProtocolState.PROPOSE,
        ProtocolState.NEGOTIATE,
        ProtocolState.COMMIT,
        ProtocolState.EXECUTE,
        ProtocolState.VERIFY,
    ):
        c.transition(st)

    c.transition(ProtocolState.EXECUTE)
    assert c.retries == 1
    c.transition(ProtocolState.VERIFY)
    c.transition(ProtocolState.EXECUTE)
    assert c.retries == 2
    c.transition(ProtocolState.VERIFY)

    with pytest.raises(ValueError):
        c.transition(ProtocolState.EXECUTE)

    c.transition(ProtocolState.FAILED)
    assert c.state == ProtocolState.FAILED


def test_schema_validation():
    ok, _ = validate_json_schema({"status": "OK", "metrics_data": {}}, ["status", "metrics_data"])
    assert ok is True
    bad, _ = validate_json_schema({"status": "OK"}, ["status", "metrics_data"])
    assert bad is False
