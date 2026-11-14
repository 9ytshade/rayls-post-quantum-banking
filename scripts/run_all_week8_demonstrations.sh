#!/usr/bin/env bash
# Week 8 Full Reproduction Runner: Post-Quantum Banking & HNDL Protocol Forensics
set -euo pipefail

export PATH="$HOME/.local/go/bin:$HOME/go/bin:$HOME/.foundry/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${WORKSPACE_ROOT}"

echo "=== STEP 1: Re-running N=500 ML-KEM-768 vs Classical Benchmarks ==="
go run scripts/benchmark_pq.go

echo "=== STEP 2: Running 1,000-Block Rayls Mainnet 72957 Telemetry Scan ==="
python3 scripts/mainnet_pq_telemetry.py

echo "=== STEP 3: Executing Deterministic Foundry Invariant Tests ==="
forge test --match-path "test/PQInvariantAudit.t.sol" -vvv

echo "=== STEP 4: Executing Live Mainnet Fork Gas Tests ==="
forge test --match-path "test/PQMainnetFork.t.sol" -vvv

echo "=== STEP 5: Executing Upstream Enygma Agreement Tests ==="
(cd "${HOME}/rayls_src/Enygma/enygma_payments/go_client/agreement" && go test -v -count=1 .)

echo "=== STEP 6: Validating Machine-Readable Empirical Datasets Gate ==="
python3 scripts/verify_datasets.py

echo "=== ALL WEEK 8 TESTS & BENCHMARKS PASSED (EXIT 0) ==="
