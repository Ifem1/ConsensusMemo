# Consensus Design

ConsensusMemo separates semantic adjudication from deterministic reuse safety.

## Leader work

For a new exact context, the leader receives the same bounded task that validators receive. It must independently return:

```json
{
  "decision": "YES | NO | INCONCLUSIVE",
  "confidence": "HIGH | MEDIUM | LOW",
  "flags": ["allowed stable flag"],
  "material_basis": "short prose explanation"
}
```

The contract normalizes casing, sorts and deduplicates flags, rejects unknown enum values, and bounds the stored explanation.

## Validator work

Validators do not merely inspect the leader output for formatting or plausibility. Each validator independently executes the same adjudication task from the original question, evidence, policy, context, and schema version.

The validator then compares its own normalized result with the leader's normalized result.

## Equivalence rule

Consensus-critical equality requires all three material fields to match:

1. `decision`
2. `confidence`
3. normalized `flags`

`material_basis` is intentionally excluded from equality. Two validators may explain the same material outcome with different prose while still agreeing on the decision, confidence band, and material risk flags.

This is comparative validation, not non-comparative approval of the leader.

## Why these fields

`decision` alone would be too weak: two validators could both say YES while disagreeing materially about uncertainty or a policy ambiguity. Exact prose equality would be too brittle. The confidence band and stable flag vocabulary provide additional semantic anchors without requiring stylistically identical explanations.

## Deterministic state boundary

No storage access occurs inside the non-deterministic callbacks. Input values are passed as plain local strings to the consensus task. After `run_nondet_unsafe` returns an accepted result, deterministic code:

- allocates the memo id;
- records the exact adjudication inputs;
- records the normalized result;
- sets creation and expiry timestamps;
- binds the canonical exact context to the memo id.

## Reuse rule

A memo is reusable only when:

- it exists;
- stored status is `ACTIVE`;
- transaction time is not past `valid_until`;
- the caller's expected question, evidence, policy, context, and schema version exactly match the stored fields.

No embedding, fuzzy comparison, LLM similarity check, or prefix matching is used for reuse.

## Fresh resolution

If a prior exact-context memo is expired, revoked, or superseded, `resolve` performs a fresh consensus adjudication and replaces the context binding with the new memo id. Historical memos remain queryable.

## Failure behavior

Malformed leader or validator JSON, unsupported decisions/confidence values, unknown flags, or material validator disagreement causes the nondeterministic consensus path to fail rather than silently persisting a weak receipt.
