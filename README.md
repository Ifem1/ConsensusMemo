# ConsensusMemo

ConsensusMemo is a standalone GenLayer Intelligent Contract primitive for creating **portable, exact-context consensus receipts** that other contracts can safely reuse.

It is intentionally **frontend-free**. The repository focuses on the contract, its consensus model, composition interface, tests, and reviewer documentation.

## Problem

Many Intelligent Contracts independently ask validators to resolve the same semantic question from the same evidence under the same rules. Re-running that adjudication wastes validator work and makes composition harder.

ConsensusMemo turns a completed GenLayer adjudication into a reusable memo that is cryptographically bound to the exact inputs that produced it:

- subject / question
- evidence
- governing policy / criteria
- context / domain separator
- adjudication schema version

A memo can only be reused when those exact bindings match and the memo is still active and unexpired.

## Core invariant

**Similarity is never enough.** ConsensusMemo never treats a merely similar question, policy, or evidence set as equivalent to a cached adjudication. The reuse key is deterministic and exact.

## Why GenLayer

The semantic decision is non-deterministic and is therefore resolved with GenLayer consensus. The leader independently classifies the supplied adjudication context; validators independently repeat the classification and must match the material decision fields. Only after consensus does deterministic code persist the memo.

The contract deliberately separates:

1. **Non-deterministic semantic work** — LLM-based adjudication inside `gl.vm.run_nondet_unsafe`.
2. **Deterministic safety logic** — input binding, hashing, replay/reuse checks, TTL bounds, revocation, supersession, and state writes.

## Decision schema

Consensus stores a bounded result:

- `decision`: `YES`, `NO`, or `INCONCLUSIVE`
- `confidence`: `HIGH`, `MEDIUM`, or `LOW`
- `material_basis`: short human-readable rationale

Validators do **not** compare prose. They independently re-run the task and require the same `decision` and `confidence`. This prevents stylistic differences from breaking consensus while keeping the material outcome strict.

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

`EXPIRED` is derived from the deterministic transaction timestamp and `valid_until`; expiry does not require a maintenance transaction.

## Public composition surface

### `resolve(...)`
Creates a new memo or returns an already-active memo for the exact same context.

### `lookup_context(...)`
Computes the exact context key and returns the memo id currently bound to it.

### `is_usable(memo_id)`
Returns true only when the memo exists, is `ACTIVE`, and has not expired.

### `matches_context(memo_id, ...)`
Lets a consuming contract prove that a memo is bound to the exact subject, evidence, policy, context, and schema version it expects.

### `revoke(memo_id)`
The creator can revoke an active memo.

### `supersede(old_memo_id, ...)`
The creator can retire an old memo and create/reuse a new memo for revised inputs.

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

if not memo_contract.is_usable(memo_id):
    raise Exception("No active consensus receipt")

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
contracts/ConsensusMemo.py      Intelligent Contract
tests/direct/                   Direct-mode and consensus tests
docs/CONSENSUS.md               Leader/validator and equivalence design
docs/SECURITY.md                Threat model and invariants
examples/consumer.py            Minimal composition example
```

## Development

Requirements: Python 3.12+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

genvm-lint check contracts/ConsensusMemo.py
pytest tests/direct/ -v
```

GenLayer's current tooling supports fast direct-mode tests without Studio and recommends validating multi-validator behavior separately in Studio/StudioNet before treating a deployment as production evidence.

## What this is not

ConsensusMemo is not:

- a generic key/value cache
- a similarity search engine
- a truth oracle
- a format-only validator
- a frontend application
- a thin wrapper around an LLM response

Its reusable primitive is the combination of **semantic consensus + exact deterministic context binding + lifecycle-controlled reuse**.

## License

MIT
