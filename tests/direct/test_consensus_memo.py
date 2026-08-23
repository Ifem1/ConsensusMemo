import json
import pytest


QUESTION = "Did the submitted release satisfy the documented acceptance criteria?"
EVIDENCE = "Release v1.2.0 is deployed. All required checks in the supplied report passed."
POLICY = "Answer YES only when the release is deployed and all required checks passed."
CONTEXT = "project=demo;release=v1.2.0"
SCHEMA = "consensus-memo/v1"
TTL = 3600

YES_RESULT = json.dumps({
    "decision": "YES",
    "confidence": "HIGH",
    "flags": [],
    "material_basis": "Deployment and required checks are both supported.",
})

NO_RESULT = json.dumps({
    "decision": "NO",
    "confidence": "HIGH",
    "flags": ["MISSING_SUPPORT"],
    "material_basis": "Required checks are not supported.",
})


def deploy(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/consensus_memo.py")
    direct_vm.sender = direct_alice
    return contract


def resolve_yes(contract, direct_vm):
    direct_vm.mock_llm(r".*independently adjudicating.*", YES_RESULT)
    return json.loads(contract.resolve(QUESTION, EVIDENCE, POLICY, CONTEXT, SCHEMA, TTL))


def test_resolve_creates_bound_memo(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_vm, direct_deploy, direct_alice)
    result = resolve_yes(contract, direct_vm)

    assert result["memo_id"] == 1
    assert result["decision"] == "YES"
    assert result["confidence"] == "HIGH"
    assert result["reused"] is False
    assert contract.is_usable(1) is True
    assert contract.matches_context(1, QUESTION, EVIDENCE, POLICY, CONTEXT, SCHEMA) is True


def test_exact_context_is_reused_without_second_adjudication(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_vm, direct_deploy, direct_alice)
    first = resolve_yes(contract, direct_vm)
    direct_vm.clear_mocks()

    second = json.loads(contract.resolve(QUESTION, EVIDENCE, POLICY, CONTEXT, SCHEMA, TTL))
    assert second["memo_id"] == first["memo_id"]
    assert second["reused"] is True


def test_changed_evidence_never_reuses_memo(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_vm, direct_deploy, direct_alice)
    first = resolve_yes(contract, direct_vm)

    direct_vm.clear_mocks()
    direct_vm.mock_llm(r".*independently adjudicating.*", YES_RESULT)
    changed = EVIDENCE + " Additional independent audit attached."
    second = json.loads(contract.resolve(QUESTION, changed, POLICY, CONTEXT, SCHEMA, TTL))

    assert second["memo_id"] != first["memo_id"]
    assert second["reused"] is False
    assert contract.matches_context(first["memo_id"], QUESTION, changed, POLICY, CONTEXT, SCHEMA) is False


def test_changed_policy_never_reuses_memo(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_vm, direct_deploy, direct_alice)
    first = resolve_yes(contract, direct_vm)

    direct_vm.clear_mocks()
    direct_vm.mock_llm(r".*independently adjudicating.*", YES_RESULT)
    changed_policy = POLICY + " Security review must also pass."
    second = json.loads(contract.resolve(QUESTION, EVIDENCE, changed_policy, CONTEXT, SCHEMA, TTL))

    assert second["memo_id"] != first["memo_id"]
    assert contract.matches_context(first["memo_id"], QUESTION, EVIDENCE, changed_policy, CONTEXT, SCHEMA) is False


def test_validator_accepts_materially_equal_result_despite_prose_change(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_vm, direct_deploy, direct_alice)
    resolve_yes(contract, direct_vm)

    direct_vm.clear_mocks()
    validator_result = json.dumps({
        "decision": "YES",
        "confidence": "HIGH",
        "flags": [],
        "material_basis": "Different wording from the validator.",
    })
    direct_vm.mock_llm(r".*independently adjudicating.*", validator_result)
    assert direct_vm.run_validator() is True


def test_validator_rejects_competing_decision(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_vm, direct_deploy, direct_alice)
    resolve_yes(contract, direct_vm)

    direct_vm.clear_mocks()
    direct_vm.mock_llm(r".*independently adjudicating.*", NO_RESULT)
    assert direct_vm.run_validator() is False


def test_validator_rejects_competing_confidence_or_flags(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_vm, direct_deploy, direct_alice)
    resolve_yes(contract, direct_vm)

    direct_vm.clear_mocks()
    direct_vm.mock_llm(r".*independently adjudicating.*", json.dumps({
        "decision": "YES",
        "confidence": "MEDIUM",
        "flags": ["POLICY_AMBIGUITY"],
        "material_basis": "Decision agrees but material confidence does not.",
    }))
    assert direct_vm.run_validator() is False


def test_expiry_makes_memo_unusable_and_allows_fresh_resolution(direct_vm, direct_deploy, direct_alice):
    direct_vm.warp("2026-01-01T00:00:00+00:00")
    contract = deploy(direct_vm, direct_deploy, direct_alice)
    direct_vm.mock_llm(r".*independently adjudicating.*", YES_RESULT)
    first = json.loads(contract.resolve(QUESTION, EVIDENCE, POLICY, CONTEXT, SCHEMA, 60))

    direct_vm.warp("2026-01-01T00:01:01+00:00")
    assert contract.is_usable(first["memo_id"]) is False
    assert contract.effective_status(first["memo_id"]) == "EXPIRED"

    direct_vm.clear_mocks()
    direct_vm.mock_llm(r".*independently adjudicating.*", YES_RESULT)
    second = json.loads(contract.resolve(QUESTION, EVIDENCE, POLICY, CONTEXT, SCHEMA, 60))
    assert second["memo_id"] != first["memo_id"]
    assert second["reused"] is False


def test_creator_can_revoke_and_non_creator_cannot(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = deploy(direct_vm, direct_deploy, direct_alice)
    memo = resolve_yes(contract, direct_vm)

    direct_vm.sender = direct_bob
    with pytest.raises(Exception, match="only memo creator"):
        contract.revoke(memo["memo_id"])

    direct_vm.sender = direct_alice
    contract.revoke(memo["memo_id"])
    assert contract.is_usable(memo["memo_id"]) is False
    assert contract.effective_status(memo["memo_id"]) == "REVOKED"


def test_supersede_requires_same_creator_and_usable_replacement(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_vm, direct_deploy, direct_alice)
    first = resolve_yes(contract, direct_vm)

    direct_vm.clear_mocks()
    direct_vm.mock_llm(r".*independently adjudicating.*", YES_RESULT)
    second = json.loads(contract.resolve(QUESTION, EVIDENCE + " v2", POLICY, CONTEXT, SCHEMA, TTL))

    contract.supersede(first["memo_id"], second["memo_id"])
    assert contract.is_usable(first["memo_id"]) is False
    assert contract.effective_status(first["memo_id"]) == "SUPERSEDED"
    old = json.loads(contract.get_memo(first["memo_id"]))
    assert old["superseded_by"] == second["memo_id"]


def test_ttl_bounds_are_enforced(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_vm, direct_deploy, direct_alice)
    with pytest.raises(Exception, match="ttl out of bounds"):
        contract.resolve(QUESTION, EVIDENCE, POLICY, CONTEXT, SCHEMA, 59)
    with pytest.raises(Exception, match="ttl out of bounds"):
        contract.resolve(QUESTION, EVIDENCE, POLICY, CONTEXT, SCHEMA, 31536001)


def test_storage_serialization_is_supported(direct_vm, direct_deploy, direct_alice):
    direct_vm.check_pickling = True
    contract = deploy(direct_vm, direct_deploy, direct_alice)
    resolve_yes(contract, direct_vm)
    assert contract.is_usable(1) is True
