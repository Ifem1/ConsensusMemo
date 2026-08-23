import os

import pytest

from gltest import get_contract_factory, get_default_account
from gltest.assertions import tx_execution_succeeded
from gltest.utils import extract_contract_address


pytestmark = pytest.mark.integration


def _factory():
    return get_contract_factory("ConsensusMemo")


def test_deploy_and_read_surface():
    """Each test deploys independently; no ordering or shared id is assumed."""
    factory = _factory()
    deployment = factory.deploy_contract_tx(account=get_default_account())
    contract = factory.build_contract(
        extract_contract_address(deployment), account=get_default_account()
    )
    print(f"DEPLOYMENT_RECEIPT={deployment}")
    print(f"DEPLOYED_CONTRACT={contract.address}")
    assert contract.lookup_context(
        args=["unseen question", "unseen evidence", "policy", "context", "v1"]
    ).call() == 0


def test_live_resolution_and_reuse():
    factory = _factory()
    deployment = factory.deploy_contract_tx(account=get_default_account())
    contract = factory.build_contract(
        extract_contract_address(deployment), account=get_default_account()
    )
    print(f"DEPLOYMENT_RECEIPT={deployment}")
    print(f"DEPLOYED_CONTRACT={contract.address}")
    args = [
        "Is the release deployed?",
        "The public release report says the release is deployed.",
        "Answer YES only when deployment is supported.",
        "integration-live-resolution",
        "consensus-memo/v1",
        3600,
    ]
    first = contract.resolve(args=args).transact()
    print(f"RESOLUTION_RECEIPT={first}")
    assert tx_execution_succeeded(first)
    memo_id = int(contract.lookup_context(args=args[:5]).call())
    assert memo_id > 0
    assert contract.is_usable(args=[memo_id]).call() is True
    second = contract.resolve(args=args).transact()
    print(f"REUSE_RECEIPT={second}")
    assert tx_execution_succeeded(second)


@pytest.mark.skipif(
    not os.getenv("CONSENSUSMEMO_RUN_LIVE_NEGATIVE"),
    reason="Set CONSENSUSMEMO_RUN_LIVE_NEGATIVE=1 to spend a live consensus transaction",
)
def test_live_negative_path_is_explicitly_opt_in():
    contract = _factory().deploy(account=get_default_account())
    receipt = contract.resolve(
        args=[
            "Does the report prove a missing requirement?",
            "The report contains no such evidence.",
            "Answer YES only when the requirement is proven.",
            "integration-live-negative",
            "consensus-memo/v1",
            3600,
        ],
        ).transact()
    assert tx_execution_succeeded(receipt)
