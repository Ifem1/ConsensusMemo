# ConsensusMemo

ConsensusMemo is a standalone GenLayer Intelligent Contract primitive for creating **portable, exact-context consensus receipts** that other contracts can safely reuse.

It is intentionally **frontend-free**. The repository focuses on the contract, its consensus model, composition interface, tests, and reviewer documentation.

## Problem

Many Intelligent Contracts independently ask validators to resolve the same semantic question from the same evidence under the same rules. Re-running that adjudication wastes validator work and makes composition harder.

ConsensusMemo turns a completed GenLayer adjudication into a reusable memo that is deterministically bound to the exact inputs that produced it:

- question
- evidence
- governing policy / criteria
- context / domain separator
- adjudication schema version

A memo can only be reused when those exact bindings match and the memo is still active and unexpired.

## Core invariant

**Similarity is never enough.** ConsensusMemo never treats a merely similar question, policy, evidence set, context, or schema version as equivalent to a prior adjudication. The canonical reuse key is deterministic and exact, and `matches_context` independently checks every stored field.

## Why GenLayer

The semantic decision is non-deterministic and is resolved with GenLayer consensus. The leader independently classifies the supplied adjudication context; validators independently perform the same classification and compare their result with the leader's material fields. Only after consensus does deterministic code persist the memo.

The contract separates:

1. **Non-deterministic semantic work** — LLM-based adjudication inside `gl.vm.run_nondet_unsafe`.
2. **Deterministic safety logic** — exact input binding, replay/reuse checks, TTL bounds, revocation, supersession, and state writes.

## Decision schema

Consensus stores a bounded result:

- `decision`: `YES`, `NO`, or `INCONCLUSIVE`
- `confidence`: `HIGH`, `MEDIUM`, or `LOW`
- `flags`: stable material flags such as `MISSING_SUPPORT` or `POLICY_AMBIGUITY`
- `material_basis`: short human-readable rationale

Validators do **not** merely approve the leader result. They independently rerun the original task. Equivalence requires the same `decision`, `confidence`, and normalized `flags`. Free-form explanation prose is deliberately excluded from equality.

## Lifecycle

```text
                create
                  |
                  v
               ACTIVE
              /      \
        revoke        supersede
           |              |
           v              v
        REVOKED       SUPERSEDED

ACTIVE --time--> EXPIRED (derived, not written)
```

`EXPIRED` is derived from GenVM's deterministic transaction timestamp and `valid_until`; expiry does not require a maintenance transaction.

## Public composition surface

### `resolve(...)`
Creates a new memo or returns an already-usable memo for the exact same context. If the prior exact-context memo is expired, revoked, or superseded, a fresh consensus adjudication is required.

### `lookup_context(...)`
Computes the canonical exact context key and returns the currently bound memo id, or `0` when none exists.

### `is_usable(memo_id)`
Returns true only when the memo exists, is `ACTIVE`, and has not expired.

### `matches_context(memo_id, ...)`
Lets a consuming contract prove that a memo is bound to the exact question, evidence, policy, context, and schema version it expects.

### `revoke(memo_id)`
The creator can revoke an active memo.

### `supersede(old_memo_id, new_memo_id)`
The creator can retire an old memo in favor of an already-usable replacement memo created by the same address.

## Example composition

A downstream Intelligent Contract can treat ConsensusMemo as a semantic cache without trusting fuzzy matching:

```python
memo_id = memo_contract.lookup_context(
    question,
    evidence,
    policy,
    context,
    schema_version,
)

if int(memo_id) == 0 or not memo_contract.is_usable(memo_id):
    raise Exception("No usable consensus receipt")

if not memo_contract.matches_context(
    memo_id,
    question,
    evidence,
    policy,
    context,
    schema_version,
):
    raise Exception("Memo binding mismatch")
```

## Repository layout

```text
contracts/consensus_memo.py     Intelligent Contract
tests/direct/                   Direct-mode and comparative-validator tests
docs/CONSENSUS.md               Leader/validator and equivalence design
docs/SECURITY.md                Threat model and invariants
examples/consumer.py            Minimal IC-to-IC composition example
SUBMISSION.md                   Reviewer-oriented category summary
```

## Development

Requirements: Python 3.12+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

genvm-lint check contracts/consensus_memo.py
pytest tests/direct/ -v
```

GenLayer's current testing tooling supports direct-mode validator capture: tests can run the leader, swap the mocked LLM response, and call `direct_vm.run_validator()` to prove that a competing validator result is rejected.

## Test coverage

The direct suite covers:

- first resolution and storage;
- exact-context memo reuse;
- changed evidence isolation;
- changed policy isolation;
- materially equivalent validator prose;
- validator rejection on a competing decision;
- validator rejection on competing confidence/flags;
- expiry and fresh re-resolution;
- creator-only revocation;
- supersession lifecycle;
- TTL bounds.

## What this is not

ConsensusMemo is not:

- a generic key/value cache;
- a similarity search engine;
- a truth oracle;
- a format-only validator;
- a frontend application;
- a non-comparative "AI says yes" wrapper.

Its reusable primitive is the combination of **semantic consensus + exact deterministic context binding + lifecycle-controlled reuse**.

## License

MIT
