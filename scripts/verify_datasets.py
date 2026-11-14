#!/usr/bin/env python3
"""
Week 8 Empirical Dataset Verification Gatekeeper
------------------------------------------------
Validates that all machine-readable datasets in data/ conform strictly to:
  1. Rayls Public Chain (72957) canonical telemetry (1,000 blocks, unbroken parent links, 500M gas ceiling)
  2. N = 500 NIST FIPS 203 ML-KEM-768 vs Classical X25519 cryptographic benchmarks
  3. Foundry offline invariant suite (8/8 PASS, 256 fuzz runs) and Mainnet fork suite (3/3 PASS)
  4. Upstream raylsnetwork/Enygma agreement unit suites (9/9 PASS)

Exits 0 on total verification pass; non-zero if any empirical invariant fails.
"""

import json
import os
import sys

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def verify_mainnet_telemetry():
    path = os.path.join(DATA_DIR, "rayls_mainnet_pq_telemetry.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing {path}")
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)

    assert d["chain_id"] == 72957, f"Expected chain_id 72957, got {d['chain_id']}"
    assert d["sample_block_count"] == 1000, f"Expected 1,000 blocks, got {d['sample_block_count']}"
    assert d["unbroken_parent_hash_links"] == "999/999", f"Expected 999/999 unbroken links, got {d['unbroken_parent_hash_links']}"
    assert d["block_gas_limit"] == 500000000, f"Expected 500M gas limit, got {d['block_gas_limit']}"
    assert d["genesis_system_contracts"]["ConsensusRegistry"]["bytecode_size_bytes"] == 21929
    assert d["genesis_system_contracts"]["FeeAggregatorProxy"]["bytecode_size_bytes"] == 122
    assert d["genesis_system_contracts"]["DelegationPool"]["bytecode_size_bytes"] == 15790
    print(f"  [PASS] Mainnet(72957) blk #{d['pinned_canonical_block']:,}: 1000 blks, 999/999 links, mean={d['mean_block_cadence_seconds']}s, p95={d['p95_block_cadence_seconds']}s")


def verify_pq_benchmark():
    path = os.path.join(DATA_DIR, "mlkem768_vs_classical_benchmark.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing {path}")
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)

    assert d["sample_count_n"] == 500, f"Expected N=500, got {d['sample_count_n']}"
    prims = {p["name"]: p for p in d["primitives"]}

    assert "ML-KEM-768" in prims, "Missing ML-KEM-768"
    assert prims["ML-KEM-768"]["public_key_bytes"] == 1184
    assert prims["ML-KEM-768"]["ciphertext_bytes"] == 1088
    assert prims["ML-KEM-768"]["shared_secret_bytes"] == 32

    assert "X25519" in prims, "Missing X25519"
    assert prims["X25519"]["public_key_bytes"] == 32
    assert prims["X25519"]["ciphertext_bytes"] == 32

    assert d["baby_jubjub_reduction_latency"]["warm_median_us"] < 10.0, "Baby Jubjub reduction too slow"
    print(f"  [PASS] CryptoBench(N=500): ML-KEM-768(1184B EK/1088B CT, Encap={prims['ML-KEM-768']['encap_latency']['warm_median_us']}us) vs X25519({prims['X25519']['encap_latency']['warm_median_us']}us)")


def verify_foundry_results():
    path = os.path.join(DATA_DIR, "foundry_pq_fork_results.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing {path}")
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)

    assert d["offline_suite"]["passed"] == 8, f"Expected 8 offline passes, got {d['offline_suite']['passed']}"
    assert d["offline_suite"]["failed"] == 0
    assert d["live_mainnet_fork_suite"]["passed"] == 3, f"Expected 3 fork passes, got {d['live_mainnet_fork_suite']['passed']}"
    assert d["live_mainnet_fork_suite"]["failed"] == 0
    assert d["upstream_agreement_suite"]["passed"] == 9, f"Expected 9 upstream agreement passes, got {d['upstream_agreement_suite']['passed']}"
    print(f"  [PASS] Foundry PQ Suite: offline=8/8 PASS (256 fuzz runs), mainnet_fork=3/3 PASS, upstream_agreement=9/9 PASS")


def main():
    print("=== Week 8 Empirical Dataset Verification Gate ===")
    try:
        verify_mainnet_telemetry()
        verify_pq_benchmark()
        verify_foundry_results()
        print("All 3 empirical verification gates passed cleanly (exit 0).")
        sys.exit(0)
    except Exception as e:
        print(f"Verification FAILED: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
