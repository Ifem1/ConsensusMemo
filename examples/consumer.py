# Illustrative composition example for another GenLayer Intelligent Contract.
# Replace the address with the deployed ConsensusMemo address.

from genlayer import *


@gl.contract_interface
class ConsensusMemoInterface:
    class View:
        def lookup_context(
            self,
            question: str,
            evidence: str,
            policy: str,
            context: str,
            schema_version: str,
        ) -> u256: ...

        def is_usable(self, memo_id: u256) -> bool: ...

        def matches_context(
            self,
            memo_id: u256,
            question: str,
            evidence: str,
            policy: str,
            context: str,
            schema_version: str,
        ) -> bool: ...

    class Write:
        pass


def require_consensus_memo(
    memo_address: Address,
    question: str,
    evidence: str,
    policy: str,
    context: str,
    schema_version: str,
) -> u256:
    memo = ConsensusMemoInterface(memo_address)
    memo_id = memo.view().lookup_context(
        question,
        evidence,
        policy,
        context,
        schema_version,
    )

    if int(memo_id) == 0:
        raise Exception("no memo for exact context")
    if not memo.view().is_usable(memo_id):
        raise Exception("memo is not active")
    if not memo.view().matches_context(
        memo_id,
        question,
        evidence,
        policy,
        context,
        schema_version,
    ):
        raise Exception("memo context mismatch")

    return memo_id
