# Deployment evidence

This file records verified evidence only.

## Canonical deployment

- Date: 2026-08-24
- Network: Studionet (`chainId 61999`)
- Method: `gltest` Studio Mode integration harness
- Public deployer address: `0x52dDf0414dd481c4D1Fe4dA570995Eab0034943e`
- Contract address: `0x77487c3DeC6Eca1467393c4634E6172c7f9C2D0A`
- Deployment transaction: `0xa5ca55d83ff1778279c7a9ccc5883178c4e434a0cf3d9827cc7996537376869a`
- Lifecycle: `ACCEPTED`
- Consensus result: `MAJORITY_AGREE`, one round
- Explorer: [Studionet explorer](https://explorer-studio.genlayer.com/address/0x77487c3DeC6Eca1467393c4634E6172c7f9C2D0A)
- Deployment source commit: `817a7098f5ab5062879f7f7c6b0890031281eda6`
- Deployed contract blob: `82b31eca9372b9f2289c1e147f8a07e6bc344a5e`

## Local verification

- `genvm-linter==0.10.0`: lint and validation passed with exit code 0.
- Direct Mode: 12 passed after the narrow test-only Windows workaround in `tests/conftest.py` for the `genlayer-test 0.29.2` temp-file cleanup bug. The initial failure was before contract loading and was not a contract failure.
- Preflight: 6/6 passed.
- GenVM lint: passed.
- SDK validation: passed.
- Studionet integration: 3 passed, 2 skipped (including the opt-in live lifecycle proof).
- Opt-in live lifecycle proof: passed independently, covering changed-context resolution, fresh exact-context reuse, revocation, and supersession on the canonical deployment.
- Negative Studionet test: passed independently.

## Runtime evidence on the canonical deployment

- Safe resolution transaction: `0xfeb52bc636c4f38b67686baa1284cca8c7c9a05596235376f460e630c5a3414d`
  - stored response: `memo_id=1`, `decision=YES`, `confidence=HIGH`, `flags=[]`, `reused=false`
  - consensus: `MAJORITY_AGREE`, three rounds, receipt status `ACCEPTED`
- Exact-context reuse transaction: `0xeae14e6107eee62ba7ebec571f89bec2035bff20273b52fe1c1bd5390d10f4b4`
  - stored response: `memo_id=1`, `decision=YES`, `confidence=HIGH`, `flags=[]`, `reused=true`
  - consensus: `MAJORITY_AGREE`, one round, receipt status `ACCEPTED`
- Negative/adversarial scenario: independently deployed disposable test instance; transaction passed and was not used as canonical deployment evidence.

Receipt status is reported exactly as returned by Studionet. `ACCEPTED` is not described as `FINALIZED`.

## Canonical live lifecycle proof

The canonical deployment was re-queried before the disposable lifecycle writes. Memo #1 remains intact: stored status `ACTIVE`, effective status `EXPIRED`, `is_usable=false`, original context binding `matches_context=true`, `valid_until=1787531390`, and `superseded_by=0`. This is expected TTL behavior: memo #1 was successfully reused while valid and later became unusable automatically when its TTL elapsed. No expiry transaction was required.

The following proof records use new disposable contexts and do not modify memo #1.

| Scenario | Memo | Write transaction | Expected invariant | Observed result | Consensus | Transaction status |
|---|---:|---|---|---|---|---|
| Changed-context isolation | #2 | `0x921d90ba9c89fc1df262d2293d7495574615105b48da60081fb927f468bca277` | New bound context creates a new memo | `YES`, `HIGH`, `[]`, `reused=false`; memo usable; new context matches; memo #1 does not match | `MAJORITY_AGREE` | `ACCEPTED` |
| Fresh exact-context reuse | #2 | `0x3917f965de096ff24938c6d8c6579fca0517b0fc4c5838e7bc08b9601fed3780` | Exact same inputs reuse existing memo | `memo_id=2`, `reused=true`; no new memo | `MAJORITY_AGREE` | `ACCEPTED` |
| Disposable memo creation for revocation | #3 | `0x3aef6a7f1e116f836d0bf9c6d841b206a8c621c854c7fb4a525e06239f0d2cc0` | New memo is initially usable | `YES`, `HIGH`, `[]`, `reused=false`; memo usable | `MAJORITY_AGREE` | `ACCEPTED` |
| Revocation | #3 | `0x2b3099324f1d8699bb7c81016817f6b2fe3184255a3d3e64f37ea9108ac1b6eb` | Creator can explicitly retire memo | `effective_status=REVOKED`; `is_usable=false` | `MAJORITY_AGREE` | `ACCEPTED` |
| Supersession old memo creation | #4 | `0x19031abb6d8bdf0dbda2408cf29a3841cc8f820798c4db9f1ba31b444ab75a2c` | Old replacement candidate is usable | `YES`, `HIGH`, `[]`, `reused=false`; memo usable | `MAJORITY_AGREE` | `ACCEPTED` |
| Supersession new memo creation | #5 | `0xe53722f2c7486a1ee45279665eb1eb4766d331fad4ef9a5f50de2beddebc8559` | New replacement candidate is usable | `YES`, `HIGH`, `[]`, `reused=false`; memo usable | `MAJORITY_AGREE` | `ACCEPTED` |
| Supersession | #4 → #5 | `0x25006b3b479b8b4277f2cf8d85b07ee5d2f8aaa5d3d7324078f2b3e51ac0dda2` | Old memo retires to replacement | old `SUPERSEDED`, unusable, `superseded_by=5`; new remains usable | `MAJORITY_AGREE` | `ACCEPTED` |

For all listed writes, the raw receipt reported GenVM execution `SUCCESS` and consensus result `MAJORITY_AGREE`. These are separate from the raw transaction lifecycle field, which reported `ACCEPTED`; no receipt in this proof is described as `FINALIZED`.
