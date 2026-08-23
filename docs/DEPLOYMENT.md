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
- Direct Mode: 11 passed after the narrow test-only Windows workaround in `tests/conftest.py` for the `genlayer-test 0.29.2` temp-file cleanup bug. The initial failure was before contract loading and was not a contract failure.

## Runtime evidence on the canonical deployment

- Safe resolution transaction: `0xfeb52bc636c4f38b67686baa1284cca8c7c9a05596235376f460e630c5a3414d`
  - stored response: `memo_id=1`, `decision=YES`, `confidence=HIGH`, `flags=[]`, `reused=false`
  - consensus: `MAJORITY_AGREE`, three rounds, receipt status `ACCEPTED`
- Exact-context reuse transaction: `0xeae14e6107eee62ba7ebec571f89bec2035bff20273b52fe1c1bd5390d10f4b4`
  - stored response: `memo_id=1`, `decision=YES`, `confidence=HIGH`, `flags=[]`, `reused=true`
  - consensus: `MAJORITY_AGREE`, one round, receipt status `ACCEPTED`
- Negative/adversarial scenario: independently deployed disposable test instance; transaction passed and was not used as canonical deployment evidence.

Receipt status is reported exactly as returned by Studionet. `ACCEPTED` is not described as `FINALIZED`.
