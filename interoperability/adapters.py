import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from trust.trust_core import create_agent_identity, generate_keypair, sign_payload, verify_signature


def build_signed_agent_card(
    name: str,
    capabilities: List[str],
    endpoint: str = "local://vireo/agent",
    priv_pem: Optional[str] = None,
    pub_pem: Optional[str] = None,
) -> Dict[str, Any]:
    if priv_pem is None or pub_pem is None:
        priv_pem, pub_pem = generate_keypair()
    did = create_agent_identity(pub_pem)
    card_body: Dict[str, Any] = {
        "did": did,
        "name": name,
        "version": "1.0.0",
        "url": endpoint,
        "capabilities": list(capabilities),
        "public_key_pem": pub_pem,
        "authentication": {"type": "ed25519_signature"},
    }
    signature = sign_payload(card_body, priv_pem)
    return {"card": card_body, "signature": signature}


def verify_agent_card(signed_card: Dict[str, Any]) -> bool:
    card = signed_card.get("card")
    sig = signed_card.get("signature")
    if not isinstance(card, dict) or not isinstance(sig, str):
        return False
    pub_pem = card.get("public_key_pem")
    expected_did = create_agent_identity(pub_pem) if isinstance(pub_pem, str) else ""
    if not pub_pem or card.get("did") != expected_did:
        return False
    return verify_signature(card, sig, pub_pem)


class A2AAdapter:
    """Discovery and messaging for A2A-compatible agents via signed agent cards."""

    def __init__(self, card_store_path: Optional[Path] = None) -> None:
        self.card_store_path = Path(card_store_path) if card_store_path is not None else None
        self._registry: List[Dict[str, Any]] = []
        self._refresh_registry()

    def _load_persisted_cards(self) -> List[Dict[str, Any]]:
        if self.card_store_path is None or not self.card_store_path.exists():
            return []
        try:
            raw = json.loads(self.card_store_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        if not isinstance(raw, list):
            return []
        return [item for item in raw if isinstance(item, dict) and verify_agent_card(item)]

    def _save_persisted_cards(self, cards: List[Dict[str, Any]]) -> None:
        if self.card_store_path is None:
            return
        self.card_store_path.parent.mkdir(parents=True, exist_ok=True)
        self.card_store_path.write_text(
            json.dumps(cards, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _refresh_registry(self) -> None:
        planner_card = build_signed_agent_card(
            name="planner",
            capabilities=["planning", "metrics_reader", "data_analysis"],
            endpoint="local://vireo/planner",
        )
        verifier_card = build_signed_agent_card(
            name="verifier",
            capabilities=["verify", "metrics_reader"],
            endpoint="local://vireo/verifier",
        )
        builtin_cards = [c for c in (planner_card, verifier_card) if verify_agent_card(c)]
        persisted_cards = self._load_persisted_cards()
        self._registry = builtin_cards + persisted_cards

    def register_agent(
        self,
        name: str,
        capabilities: List[str],
        endpoint: str = "local://vireo/custom-agent",
    ) -> Dict[str, Any]:
        cleaned_name = name.strip()
        if not cleaned_name:
            raise ValueError("Agent name must not be empty")
        cleaned_caps = [c.strip() for c in capabilities if c and c.strip()]
        if not cleaned_caps:
            cleaned_caps = ["metrics_reader"]
        cleaned_endpoint = endpoint.strip() or f"local://vireo/{cleaned_name}"

        signed_card = build_signed_agent_card(
            name=cleaned_name,
            capabilities=cleaned_caps,
            endpoint=cleaned_endpoint,
        )
        if not verify_agent_card(signed_card):
            raise ValueError("Generated agent card failed Ed25519 signature or DID verification")

        persisted = self._load_persisted_cards()
        persisted.append(signed_card)
        self._save_persisted_cards(persisted)
        self._refresh_registry()
        return signed_card["card"]

    def list_all_agents(self) -> List[Dict[str, Any]]:
        result: List[Dict[str, Any]] = []
        for entry in self._registry:
            if verify_agent_card(entry):
                result.append(entry["card"])
        return result

    def discover_agents(self, capability: str) -> List[Dict[str, Any]]:
        matched: List[Dict[str, Any]] = []
        for entry in self._registry:
            if not verify_agent_card(entry):
                continue
            card = entry["card"]
            if not capability or capability in card.get("capabilities", []):
                matched.append(card)
        return matched

    def send_envelope(self, target_did: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "delivered", "target": target_did, "keys": list(payload.keys())}


class MCPAdapter:
    """Scoped tool and data access via MCP."""

    def invoke_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        return {"tool": tool_name, "ok": True, "args": arguments}


class ExternalAgentProxy:
    """External worker agent. honest=False simulates a tampering executor."""

    def __init__(self, agent_id: str, framework: str = "CrewAI", honest: bool = True) -> None:
        self.agent_id = agent_id
        self.framework = framework
        self.honest = honest

    def execute(self, task_payload: Dict[str, Any]) -> Dict[str, Any]:
        output = "Completed: " + str(task_payload.get("objective", "task"))
        if not self.honest:
            output = "TAMPERED: " + output
        return {"agent_id": self.agent_id, "framework": self.framework, "output": output}


class ProtocolBridge:
    """Coordinates external transport (A2A) and tool layer (MCP) under Vireo contracts."""

    def __init__(self, card_store_path: Optional[Path] = None) -> None:
        self.a2a = A2AAdapter(card_store_path=card_store_path)
        self.mcp = MCPAdapter()

    def dispatch(self, target_did: str, tool_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        tool_res = self.mcp.invoke_tool(tool_name, payload)
        a2a_res = self.a2a.send_envelope(target_did, {"payload": payload, "tool_result": tool_res})
        return {"mcp": tool_res, "a2a": a2a_res, "payload": payload}
