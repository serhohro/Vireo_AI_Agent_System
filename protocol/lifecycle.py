from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Set


class ProtocolState(str, Enum):
    DISCOVER = "DISCOVER"
    PROPOSE = "PROPOSE"
    NEGOTIATE = "NEGOTIATE"
    COMMIT = "COMMIT"
    EXECUTE = "EXECUTE"
    VERIFY = "VERIFY"
    DONE = "DONE"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


ALLOWED: Dict[ProtocolState, Set[ProtocolState]] = {
    ProtocolState.DISCOVER: {ProtocolState.PROPOSE},
    ProtocolState.PROPOSE: {ProtocolState.NEGOTIATE, ProtocolState.CANCELLED},
    ProtocolState.NEGOTIATE: {ProtocolState.COMMIT, ProtocolState.PROPOSE, ProtocolState.CANCELLED},
    ProtocolState.COMMIT: {ProtocolState.EXECUTE, ProtocolState.CANCELLED},
    ProtocolState.EXECUTE: {ProtocolState.VERIFY, ProtocolState.CANCELLED},
    ProtocolState.VERIFY: {ProtocolState.DONE, ProtocolState.EXECUTE, ProtocolState.FAILED},
}


@dataclass
class CommitmentContract:
    task_id: str
    initiator_did: str
    executor_did: str
    objective: str
    verification_criteria: Dict[str, Any] = field(default_factory=dict)
    state: ProtocolState = ProtocolState.DISCOVER
    retries: int = 0
    max_retries: int = 2
    evidence: Dict[str, Any] = field(default_factory=dict)

    def transition(self, next_state: ProtocolState) -> None:
        allowed = ALLOWED.get(self.state, set())
        if next_state not in allowed:
            raise ValueError(f"Invalid transition: {self.state.value} -^> {next_state.value}")
        if self.state == ProtocolState.VERIFY and next_state == ProtocolState.EXECUTE:
            if self.retries >= self.max_retries:
                raise ValueError("Retry limit reached")
            self.retries += 1
        self.state = next_state
