# Integration guide

ConsensusMemo is intended to be consumed by another Intelligent Contract as a reusable semantic receipt.

1. Call `lookup_context(question, evidence, policy, context, schema_version)`.
2. Require a non-zero memo id and `is_usable(memo_id == True)`.
3. Call `matches_context` with the exact same five binding values.
4. Read `get_memo(memo_id)` and gate downstream behaviour on its stable `decision`, `confidence`, and `flags` fields.

If no usable exact-context memo exists, call `resolve(...)` and wait for consensus. A consumer must not treat `material_basis` as a consensus-critical field, and must fail closed on missing, expired, revoked, superseded, or binding-mismatched memos.

The repository includes a minimal illustrative consumer in `examples/consumer.py`; it is documentation code, not a second deployable contract.
