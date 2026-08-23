"""Dependency-free structural preflight for reviewers and builders."""
from pathlib import Path

source = Path("contracts/consensus_memo.py").read_text(encoding="utf-8")
checks = {
    "one canonical contract": source.count("class ConsensusMemo(") == 1,
    "consensus primitive present": "run_nondet_unsafe" in source,
    "validator compares material fields": "_equivalent" in source,
    "exact context binding": "context_bindings" in source and "_matches" in source,
    "bounded inputs": "MAX_EVIDENCE_CHARS" in source and "MAX_POLICY_CHARS" in source,
    "terminal lifecycle": "STATUS_REVOKED" in source and "STATUS_SUPERSEDED" in source,
}
for name, passed in checks.items():
    print(("PASS" if passed else "FAIL") + " - " + name)
if not all(checks.values()):
    raise SystemExit(1)
print(f"Preflight: {sum(checks.values())}/{len(checks)} PASS")
