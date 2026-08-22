# Security Model

## Security objective

ConsensusMemo must never let a downstream contract reuse a semantic decision for materially different adjudication inputs.

## Invariants

### 1. Exact binding

A reusable memo is bound to the exact bytes of:

- question
- evidence
- policy
- context
- schema version

The canonical context key is deterministic JSON with sorted keys, and `matches_context` independently compares every stored field. Semantic similarity is never sufficient.

### 2. Consensus before mutation

A new memo is written only after GenLayer consensus returns an accepted normalized adjudication. Storage reads/writes are kept outside the non-deterministic callbacks.

### 3. Independent validator result

Validators independently solve the original task. They do not merely rate, approve, or format-check the leader result.

### 4. Bounded inputs

Question, evidence, policy, context, schema version, TTL, and stored explanation all have explicit bounds. This limits state growth and prevents one call from supplying unbounded adjudication material.

### 5. Expiry is deterministic

Expiry uses GenVM's deterministic transaction timestamp. All validators executing the same transaction observe the same time.

### 6. Revocation authority

Only the memo creator can revoke or supersede its memo. Supersession requires a usable replacement created by the same address.

### 7. History is retained

Revoked, superseded, and expired records remain readable. Their state cannot be confused with an active reusable receipt through `is_usable`.

## Threats considered

### Prompt injection in supplied data

Every input section is explicitly marked as untrusted application data. The task instructs validators not to follow embedded instructions and to treat the policy as governing text only.

### Fuzzy-cache poisoning

There is no fuzzy cache. A single changed character in any bound input produces a different canonical context key, and stored fields must also match exactly.

### Reusing stale conclusions

Every memo has a bounded TTL. Expired memos fail `is_usable`; resolving the same context after expiry requires fresh consensus.

### Malformed model output

The normalizer rejects invalid decision values, confidence bands, flag types, unknown flags, non-string basis values, and malformed JSON.

### Leader-only classification

Prevented by comparative validation: validators generate their own decision, confidence, and flags and compare them with the leader.

### Explanation instability

Free-form explanation text is not consensus-critical. This prevents harmless wording variation from causing disagreement while material fields remain strict.

## Known trade-offs

The canonical exact-context key stores the complete adjudication context as a TreeMap key rather than relying on a hidden or caller-supplied digest. This is intentionally simple and collision-free at the application layer, but it means keys can be large. Input bounds keep this finite.

ConsensusMemo does not prove that evidence itself is authentic. The governing caller decides what evidence to submit; validators decide only what that supplied evidence means under the supplied policy. Applications needing authenticated sources should compose ConsensusMemo with a source-verification primitive or restrict evidence construction upstream.
