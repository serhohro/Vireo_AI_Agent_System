import base64
import hashlib
import json
from typing import Any, Iterable, Set
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def canonical_bytes(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")


def generate_keypair() -> tuple:
    key = Ed25519PrivateKey.generate()
    priv = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode("utf-8")
    pub = key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")
    return priv, pub


def create_agent_identity(pub_pem: str, method: str = "did:vireo") -> str:
    key = serialization.load_pem_public_key(pub_pem.encode("utf-8"))
    raw = key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    return method + ":" + hashlib.sha256(raw).hexdigest()[:32]


def sign_payload(payload: Any, priv_pem: str) -> str:
    key = serialization.load_pem_private_key(priv_pem.encode("utf-8"), password=None)
    return base64.b64encode(key.sign(canonical_bytes(payload))).decode("ascii")


def verify_signature(payload: Any, signature: str, pub_pem: str) -> bool:
    key = serialization.load_pem_public_key(pub_pem.encode("utf-8"))
    try:
        key.verify(base64.b64decode(signature), canonical_bytes(payload))
        return True
    except Exception:
        return False


def compute_artifact_hash(artifact: Any) -> str:
    return hashlib.sha256(canonical_bytes(artifact)).hexdigest()


def check_permissions(granted_scopes: Iterable[str], required_scopes: Iterable[str]) -> bool:
    granted: Set[str] = set(granted_scopes)
    return set(required_scopes).issubset(granted)
