import os

import pytest

from gltest import get_contract_factory, get_default_account


CANONICAL = "0x77487c3DeC6Eca1467393c4634E6172c7f9C2D0A"
QUESTION = "Is the release deployed?"
EVIDENCE = "The public release report says the release is deployed."
POLICY = "Answer YES only when deployment is supported."
CONTEXT = "integration-live-resolution"
SCHEMA = "consensus-memo/v1"


def test_canonical_memo_one_read_check():
    contract = get_contract_factory("ConsensusMemo").build_contract(
        CANONICAL, account=get_default_account()
    )
    memo = contract.get_memo(args=[1]).call()
    usable = contract.is_usable(args=[1]).call()
    matches = contract.matches_context(
        args=[1, QUESTION, EVIDENCE, POLICY, CONTEXT, SCHEMA]
    ).call()
    status = contract.effective_status(args=[1]).call()
    print(f"CANONICAL_MEMO={memo}")
    print(f"CANONICAL_USABLE={usable}")
    print(f"CANONICAL_MATCHES={matches}")
    print(f"CANONICAL_STATUS={status}")
    assert usable is False
    assert matches is True
    assert status == "EXPIRED"
    assert '"valid_until":' in memo


@pytest.mark.skipif(
    not os.getenv("CONSENSUSMEMO_LIVE_PROOF"),
    reason="Set CONSENSUSMEMO_LIVE_PROOF=1 to run disposable live writes",
)
def test_continue_canonical_lifecycle_from_memo_two():
    contract = get_contract_factory("ConsensusMemo").build_contract(
        CANONICAL, account=get_default_account()
    )
    ttl = 86400
    base = [
        "Does the submitted report support the stated requirement?",
        "The public report states that the requirement is satisfied.",
        "Answer YES only when the supplied report supports the requirement.",
        "project=consensusmemo-live-proof;case=changed-context-v1",
        "consensus-memo/v1",
        ttl,
    ]
    reuse = contract.resolve(args=base).transact()
    print(f"FRESH_REUSE_RECEIPT={reuse}")
    assert reuse.get("status_name") == "ACCEPTED"

    revoke_args = [*base[:3], "project=consensusmemo-live-proof;case=revoke-v1", base[4], ttl]
    def next_unused_id():
        candidate = 1
        while True:
            try:
                contract.get_memo(args=[candidate]).call()
            except Exception:
                return candidate
            candidate += 1

    revoke_id = next_unused_id()
    revoke_create = contract.resolve(args=revoke_args).transact()
    assert '"memo_id":' in contract.get_memo(args=[revoke_id]).call()
    revoke_tx = contract.revoke(args=[revoke_id]).transact()
    print(f"REVOKE_CREATE={revoke_create}")
    print(f"REVOKE_TX={revoke_tx}")
    assert contract.effective_status(args=[revoke_id]).call() == "REVOKED"
    assert contract.is_usable(args=[revoke_id]).call() is False

    old_args = [*base[:3], "project=consensusmemo-live-proof;case=supersede-old-v1", base[4], ttl]
    new_args = [*base[:3], "project=consensusmemo-live-proof;case=supersede-new-v1", base[4], ttl]
    old_id = next_unused_id()
    old_create = contract.resolve(args=old_args).transact()
    assert '"memo_id":' in contract.get_memo(args=[old_id]).call()
    new_id = next_unused_id()
    new_create = contract.resolve(args=new_args).transact()
    assert '"memo_id":' in contract.get_memo(args=[new_id]).call()
    supersede_tx = contract.supersede(args=[old_id, new_id]).transact()
    print(f"SUPERSEDE_OLD_CREATE={old_create}")
    print(f"SUPERSEDE_NEW_CREATE={new_create}")
    print(f"SUPERSEDE_TX={supersede_tx}")
    old_memo = contract.get_memo(args=[old_id]).call()
    assert contract.effective_status(args=[old_id]).call() == "SUPERSEDED"
    assert contract.is_usable(args=[old_id]).call() is False
    assert contract.is_usable(args=[new_id]).call() is True
    assert f'"superseded_by":{new_id}' in old_memo
