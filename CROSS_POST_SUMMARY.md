# Cross-Post Package: Can Post-Quantum Cryptography Protect Private EVMs from Harvest-Now-Decrypt-Later Attacks?

---

## Part 1: Twitter / X Long-Form Master Thread

### Post 1/8 (Hook & Scope)
Most discussions around institutional blockchain privacy focus on zero-knowledge proofs. But there is a silent systemic threat: **Harvest-Now-Decrypt-Later (HNDL)**.

Corporate bonds, mortgages, and sovereign debt (like Brazil's Drex TPFt) have **10-to-30-year maturities**. If an adversary intercepts classical encrypted transactions today, Shor's algorithm on a quantum computer in the 2030s breaks banking secrecy retroactively.

I evaluated Rayls' post-quantum architecture (**NIST FIPS 203 ML-KEM-768**) across upstream Enygma source code, an N=500 benchmark, and live Rayls Mainnet (`Chain ID 72957`). Here is what the empirical data proves:

### Post 2/8 (Live Mainnet Chain 72957 Telemetry)
First, I grounded my gas and latency assumptions against live **Rayls Public Chain Mainnet** (`https://mainnet-rpc.rayls.com`):
- Pinned canonical tip block `#14,548,825` with `0` blocks of lag to `finalized` tag
- 1,000 consecutive blocks (`999/999` unbroken parent links) averaged `1.3413s` cadence (`1s` median, `2.0s` p95)
- `57.60 Gwei` base gas price under a `500,000,000` block gas ceiling
- Genesis contracts verified: ConsensusRegistry (`21,929 B`), FeeAggregatorProxy (`122 B`), and DelegationPool (`15,790 B`).

### Post 3/8 (Upstream Source Forensics: Strict 1,184-Byte Key Boundaries)
In `raylsnetwork/Enygma` (`@ a9b06c00`), on-chain contract `Enygma.sol` line 529 strictly enforces post-quantum encapsulation key sizes:
`if (viewKey.length != 0 && viewKey.length != 1184) revert InvalidViewKeyLength();`

This eliminates mixed-security downgrade attacks: banks cannot register weak 32-byte (`X25519`) or 65-byte (`P-256`) classical keys. Only legitimate 0-byte non-circuit relayers or full 1,184-byte ML-KEM-768 view keys are accepted by EVM state.

### Post 4/8 (Counter-Intuitive Latency Finding: ML-KEM-768 Consistently Outperforms X25519)
I ran an $N = 500$ benchmark comparing NIST FIPS 203 ML-KEM-768 against classical X25519 and P-256 in Go on a consumer 2.40 GHz CPU:
- **ML-KEM-768 Warm Median:** Keygen = `178.7 us`, Encap = **`195.9 us`**, Decap = `177.9 us` (Total: `552.5 us`)
- **X25519 Warm Median:** Keygen = `104.4 us`, Encap = **`211.7 us`**, Decap = `103.1 us` (Total: `419.2 us`)
- **P-256 Warm Median:** Keygen = `32.1 us`, Encap = `151.1 us`, Decap = `119.4 us` (Total: `302.6 us`)

Lattice-based ML-KEM encapsulation consistently executes faster than classical X25519 (`195.9 us` vs `211.7 us` warm median; up to `161.0 us` vs `207.7 us` in initial runs; `257.0 us` vs `283.5 us` distribution mean)! Matrix-vector operations over polynomial rings execute faster on standard CPUs than multi-precision elliptic curve scalar multiplications. Total handshake takes under 0.6 ms, fully preserving real-time banking SLAs.

### Post 5/8 (Security Audit Discovery: `Fix M-11` in `agreement/manager.go`)
Auditing Enygma's pairwise key agreement engine revealed three vital security audit remediations:
1. **Defect 1:** Lower bank ID always leads (`GetOrEstablish`), higher bank ID follows (`GetOrAccept`), preventing divergent cache keys.
2. **Defect 2 (FIPS 203 Implicit Rejection Fix):** FIPS 203 outputs pseudorandom keys on corrupted ciphertexts with `err == nil`. Enygma prevents silent ledger desync by publishing `id = SHA-256("enygma-view-key-confirm-v1:" || rawSS)`, which the follower validates in constant time.
3. **Defect 3:** Eliminating unilateral peer private seed fabrication.

### Post 6/8 (Lattice-to-ZK Field Reduction in 1.20 Microseconds)
ML-KEM outputs a 32-byte shared secret, but Baby Jubjub zero-knowledge circuits require scalar field elements bounded by subgroup order `curveP`.

Enygma bridges lattice cryptography to ZK in `1.20 us` using domain-separated reduction:
`Scalar = SHA-256("enygma-view-key-v1:" || rawSS) mod curveP`
where `curveP = 2736030358979909402780800718157159386076813972158567259200215660948447373041`.
This feeds directly into Groth16 blinding factors with zero computational friction.

### Post 7/8 (Live Fork Gas & EVM Calldata Economics)
An 1,184-byte view key is 37x larger than classical keys. Under EIP-2028 (16 gas per non-zero calldata byte), calldata costs `18,944 gas`.

Forking live Rayls Mainnet (`72957`) revealed:
- **On-chain View-Key Registration:** `308,164` total gas (`0.01775 RLS` at 57.6 Gwei)
- **Pairwise Post-Quantum Agreement:** `251,561` total gas (`0.01449 RLS`)
- **Net Calldata Delta:** Just `18,432` gas (`0.00106 RLS`), less than $0.0002!

Post-quantum security adds negligible economic friction to institutional balance sheets.

### Post 8/8 (Reproducibility & Open Source)
Full intellectual honesty: local KEM benchmarks prove mathematical and operational feasibility, while statutory legal finality (CPMI-IOSCO Principle 8) remains anchored in central bank operational frameworks outside EVM code.

Every contract, test, benchmark dataset, hardware pre-flight spec, and single-command reproduction script (`scripts/record_demo_showcase.sh`) is open source:

https://github.com/9ytshade/rayls-post-quantum-banking

---

## Part 2: Discord Quest Submission Format

**Submission Title:** Week 8 Deep Dive - Can Post-Quantum Cryptography Protect Private EVMs from Harvest-Now-Decrypt-Later Attacks?

**GitHub Repository:** https://github.com/9ytshade/rayls-post-quantum-banking

**Master Technical Article:** https://github.com/9ytshade/rayls-post-quantum-banking/blob/main/POST_QUANTUM_BANKING_HNDL_RAYLS_DEEP_DIVE.md

**Core Summary:**
In this investigation, I evaluated Rayls' post-quantum cryptographic architecture (**NIST FIPS 203 ML-KEM-768**) across upstream open-source codebases (`raylsnetwork/Enygma @ a9b06c00`), live **Rayls Public Chain Mainnet (`Chain ID 72957`)** RPC telemetry, an $N = 500$ benchmark suite, and an isolated Foundry invariant testbench (`PQAccountRegistry.sol`).

**Verified Empirical Highlights:**
- **Live Mainnet 72957 Telemetry:** Pinned canonical block `#14,548,825` with `0` blocks finalized lag, 1,000 blocks scanned (`999/999` unbroken parent links, `1.3413s` mean cadence), `57.60 Gwei` gas price, `500M` gas ceiling, and verified Genesis bytecodes (`21,929 B` / `122 B` / `15,790 B`).
- **Counter-Intuitive Latency Finding ($N=500$):** Measured that ML-KEM-768 encapsulation (`195.9 us` warm median / `257.0 us` mean) consistently outperforms classical X25519 (`211.7 us` warm median / `283.5 us` mean; up to `161.0 us` vs `207.7 us` in initial runs), with a sub-millisecond total handshake (`552.5 us`), preserving banking SLAs.
- **Upstream Audit Forensics (`Fix M-11` in `agreement/manager.go`):** Audited remediations for leader directionality (lower ID leads), constant-time mutual confirmation hash tags to prevent FIPS 203 implicit rejection desynchronization, and eliminating peer key fabrication.
- **Lattice-to-ZK Baby Jubjub Field Reduction:** Proved post-quantum shared secrets reduce modulo `curveP` in **`1.20 us`** (`1.4 us` p95) under tag `"enygma-view-key-v1:"`.
- **Foundry Invariant & Mainnet Fork Results:** 8/8 passing offline invariant tests (`CRIT-PQ1` to `CRIT-PQ4`, `256` fuzz runs), and 3/3 passing live Mainnet fork tests measuring **`308,164` gas** (`0.01775 RLS`) for an 1,184-byte view-key registration and **`251,561` gas** for pairwise agreement (`verify_datasets.py` exit 0).

**Artifacts & Reproducibility:**
- Technical Monograph & Hardware/Setup Guide: `POST_QUANTUM_BANKING_HNDL_RAYLS_DEEP_DIVE.md`
- Terminal Demonstration Video: `assets/terminal_demo_showcase.mp4` (4.75 MB, complete verification run covering all 6 stages).
- Visual Diagrams (Signature Gradient `#B49AFF -> #ECFB3E`): `assets/cover_image_post_quantum.png`, `assets/diagram_1_hndl_threat_model.png`, `assets/diagram_2_mlkem_zk_pipeline.png`, `assets/diagram_3_pq_empirical_benchmarks.png`
- Automated Empirical Demonstration Script: `bash scripts/record_demo_showcase.sh` (`[STAGE 1/6]` Pre-flight Hardware/Tools -> `[STAGE 2/6]` Upstream Code Forensics -> `[STAGE 3/6]` Live Mainnet Telemetry -> `[STAGE 4/6]` Live Crypto Benchmarks -> `[STAGE 5/6]` Offline Foundry Invariants -> `[STAGE 6/6]` Live Fork Gas & Upstream Suite), or modularly via `bash scripts/run_research_stage.sh [1-6|all]`
