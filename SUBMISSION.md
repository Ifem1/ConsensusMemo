# ConsensusMemo — Standalone Intelligent Contract Submission

## Category

Standalone GenLayer Intelligent Contract / reusable contract primitive.

## Canonical Studionet proof

- Address: `0x77487c3DeC6Eca1467393c4634E6172c7f9C2D0A`
- Deployment transaction: `0xa5ca55d83ff1778279c7a9ccc5883178c4e434a0cf3d9827cc7996537376869a`
- Lifecycle: `ACCEPTED`; consensus result `MAJORITY_AGREE`
- Safe resolution: `0xfeb52bc636c4f38b67686baa1284cca8c7c9a05596235376f460e630c5a3414d`
- Exact-context reuse: `0xeae14e6107eee62ba7ebec571f89bec2035bff20273b52fe1c1bd5390d10f4b4`

The full evidence boundary and source-parity record are maintained in `docs/DEPLOYMENT.md`.

The canonical live proof now covers semantic settlement, exact-context reuse, changed-context isolation, automatic TTL expiry, explicit revocation, and explicit supersession. Memo #1 remains untouched; lifecycle demonstrations use disposable memos #2–#5 and are recorded with raw `ACCEPTED` transaction status, GenVM `SUCCESS`, and `MAJORITY_AGREE` consensus results.

## One-line purpose

ConsensusMemo lets other Intelligent Contracts reuse a previously settled semantic decision only when the exact question, evidence, policy, context, and schema version still match and the receipt remains active and unexpired.

## Why it matters beyond a demo

GenLayer applications often repeat the same semantic adjudication in multiple contracts or workflows. ConsensusMemo provides a common on-chain receipt layer so settled decisions can be composed safely instead of re-running identical validator work.

## Why GenLayer is required

The core decision is semantic and non-deterministic: validators must interpret evidence under a governing policy. The leader produces `decision`, `confidence`, and stable material flags. Validators independently repeat the adjudication and compare those material fields. A validator is not asked merely to approve the leader.

After consensus, all persistence and reuse rules are deterministic.

## State design

Each memo stores:

- exact adjudication inputs;
- creator;
- normalized consensus result;
- creation timestamp;
- expiry timestamp;
- lifecycle status;
- optional superseding memo id.

Lifecycle states are `ACTIVE`, `REVOKED`, `SUPERSEDED`, with `EXPIRED` derived deterministically from transaction time.

## Reuse safety

A prior memo is reusable only if:

1. it is active;
2. it is not expired;
3. every expected input matches exactly.

There is no fuzzy or semantic cache lookup.

## Validator equivalence

A validator independently produces a second adjudication. Equivalence requires equality of:

- decision;
- confidence band;
- sorted stable material flags.

Free-form rationale may differ.

## Builder-facing interface

- `resolve(...)`
- `lookup_context(...)`
- `is_usable(memo_id)`
- `matches_context(memo_id, ...)`
- `get_memo(memo_id)`
- `effective_status(memo_id)`
- `revoke(memo_id)`
- `supersede(old_memo_id, new_memo_id)`

## Tests

The direct suite covers exact reuse, changed-input isolation, validator agreement/disagreement, expiry and fresh adjudication, revocation, supersession, and TTL limits.

## Scope

No frontend is included by design. ConsensusMemo is intended to be consumed by other Intelligent Contracts and applications as infrastructure.
