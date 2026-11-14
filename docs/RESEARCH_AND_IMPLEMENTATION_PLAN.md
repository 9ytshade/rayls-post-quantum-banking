# Research & Implementation Plan: Post-Quantum Banking & Neutralizing Harvest-Now-Decrypt-Later (HNDL) Attacks on Rayls

> **Document Status:** Active Production Plan  
> **Target Week:** The Rail Community Content & Research Quest - Week 8  
> **Core Topic:** Post-Quantum Key Encapsulation (NIST FIPS 203 ML-KEM-768), Harvest-Now-Decrypt-Later (HNDL) Threat Modeling, Upstream Enygma View-Key Forensics, and EVM Calldata Economics  
> **Master Audit Playbook Version:** 1.0 (All 25 Pre-Flight Gates Enforced)  
> **Author:** Independent Technical Researcher (9ytshade)  

---

## 🏛️ Executive Summary & Institutional Context

In institutional finance, confidential debt instruments, interbank credit facilities, sovereign bonds (such as Brazil's Treasury TPFt in the Drex pilot), and syndicated loans carry contractual lifespans of **10 to 30 years**. Under classical public-key cryptography (RSA, ECDH, secp256k1), an adversary who passively records encrypted network payloads today can store the ciphertexts until cryptanalytically relevant quantum computers (CRQCs) running Shor's algorithm become operational in the 2030s. This systemic attack vector is known as **Harvest-Now-Decrypt-Later (HNDL)**.

For central banks and commercial financial institutions bound by statutory secrecy laws (Brazil *Lei Complementar 105/2001*, EU *GDPR Articles 5/17*, and US *GLBA*), HNDL is not a distant future risk: **a 30-year bond transaction executed and recorded on-chain in 2026 whose confidentiality is broken in 2038 violates banking secrecy retroactively.**

Rayls addresses this systemic hazard in its **Enygma Privacy Framework** by integrating **NIST FIPS 203 ML-KEM-768** (formerly CRYSTALS-Kyber-768), standardized by NIST in August 2024. In this investigation, I evaluate how Rayls bridges post-quantum lattice-based key encapsulation with zero-knowledge EVM execution:
1. **Onchain Storage & Calldata Rules (`Enygma.sol`):** Strictly enforces `viewKey.length == 1184` bytes for all participating banking accounts, rejecting malformed or classical keys.
2. **Upstream Pairwise Key Agreement (`agreement/manager.go`):** Audits real production security fixes (**Fix M-11 defects 1, 2, and 3**) that resolve FIPS 203 implicit rejection desynchronization, leader/follower deadlock, and peer key fabrication.
3. **Lattice-to-ZK Field Mapping:** Reduces the 32-byte decapsulated shared secret modulo the **Baby Jubjub subgroup order** (`curveP = 2736030358979909402780800718157159386076813972158567259200215660948447373041`) under a domain-separated SHA-256 tag (`enygma-view-key-v1:`).
4. **Empirical Benchmarks & Mainnet 72957 Economics:** Compares $N=500$ runs of ML-KEM-768 against classical X25519/secp256k1 on a consumer CPU, models memory allocations, and calculates on-chain gas costs on a live Rayls Public Chain (`Chain ID 72957`) fork at 48 Gwei.

---

## 🔬 Master Audit Playbook Gatekeeper (25/25 Pre-Flight Requirements)

| Gate # | Playbook Requirement | Concrete Implementation in Week 8 |
| :---: | :--- | :--- |
| **Gate 1.1** | Explicit Prototype Labeling | Custom contract named `PQAccountRegistry.sol` and explicitly labeled *"Architectural Prototype & Illustrative Invariant Testbench"*. |
| **Gate 1.2** | Scope Declaration | Formal disclaimer separating local EVM testbench from closed-source enterprise node deployments. |
| **Gate 1.3** | Real Cryptographic Tests | Benchmarks unmodified upstream `filippo.io/mlkem768` (FIPS 203) and Baby Jubjub field reductions directly in Go. |
| **Gate 1.4** | Zero Invented Numbers | All latency (ms/us), gas units, and byte sizes derived from deterministic $N=500$ execution. |
| **Gate 1.5** | Scenario Assumptions | Any hypothetical network overhead calculation tagged with explicit assumptions. |
| **Gate 1.6** | Decimal Precision | Exact gas prices (48.0 Gwei), byte sizes (1,184 B EK, 1,088 B CT), and gas units. |
| **Gate 1.7** | RPC Finality Boundary | Single-endpoint RPC tag parity framed as node state, not multi-node Byzantine consensus. |
| **Gate 1.8** | Legal Finality Boundary | CPMI-IOSCO Principle 8 framing applied: cryptographic state commitments != statutory judicial discharge. |
| **Gate 1.9** | Gas vs TPS Distinction | 500M block gas limit on Chain 72957 treated as computational headroom, not realized TPS. |
| **Gate 1.10** | MEV Nuance | Calldata entropy framed as payload privacy mitigation, not elimination of all validator timing analysis. |
| **Gate 1.11** | Topology Decoupling | Private Subnet pairwise KEM agreement decoupled from Public L1 account registration. |
| **Gate 2.1** | Forensic Discovery #1 | Audit of `Fix M-11 defect 2`: FIPS 203 implicit rejection vulnerability and the `enygma-view-key-confirm-v1:` hash check. |
| **Gate 2.2** | Forensic Discovery #2 | `Enygma.sol` line 529 strict `1184` byte length enforcement vs empty relayer keys. |
| **Gate 2.3** | Forensic Discovery #3 | Direct reduction of lattice secrets into Baby Jubjub scalar field `curveP` for ZK circuit blinding factors. |
| **Gate 2.4** | Counterfactual Tests | Guard-ON vs Guard-OFF tests modeling invalid view key lengths, corrupted ciphertexts, and replay attacks. |
| **Gate 2.5** | Statistical Scale | $N \ge 500$ runs for Go KEM benchmarks and 1,000 blocks for Mainnet cadence telemetry. |
| **Gate 3.1** | GitHub Actions CI | Automated `.github/workflows/verify.yml` with 3 jobs (Foundry, Upstream Go, Data Verification). |
| **Gate 3.2** | Raw JSON Datasets | Machine-readable datasets saved in `data/` with pinned timestamps and hashes. |
| **Gate 3.3** | One-Line Reproduction | Master scripts `record_demo_showcase.sh` and `run_all_week8_demonstrations.sh`. |
| **Gate 3.4** | Brand Compliance | Noir Ventures palette with Light-Theme Signature Gradient (`#B49AFF -> #ECFB3E`). |
| **Gate 3.5** | Mobile Legibility | All diagram fonts >= 14pt, zero clipping, 30px padding on cards. |
| **Gate 3.6** | Social Safe Zones | 1600x900px canvas with bottom 120px clearance for mobile X feed. |
| **Gate 3.7** | Screen-Recording Package | Checklist covering Check 0 (Hardware/Tools) through Check 4 (Pass output) in <= 60s. |
| **Gate 4.1** | Four-Category Matrix | Evidence matrix separated into: Onchain RPC, Local Upstream, Invariant Testbench, and Docs. |
| **Gate 4.2** | Plain-English Takeaways | 1-2 line non-technical summary following every code block, table, and technical section. |

---

## 🗺️ 8-Phase Execution Roadmap

### Phase 1: Institutional Framing & Search Intent Alignment
- Define target research question: *"Can Post-Quantum Cryptography Protect Private EVMs from Harvest-Now-Decrypt-Later Attacks?"*
- Connect long-duration sovereign bonds (TPFt), mortgage-backed securities, and syndicated credit to the HNDL risk window.
- Map statutory banking secrecy mandates (Brazil LC 105/2001, GDPR Art. 5/17, US GLBA) against retroactive quantum decryption.

### Phase 2: Upstream Codebase Forensics (Enygma & Sovereign)
- Audit `Enygma.sol` line 529: `if (viewKey.length != 0 && viewKey.length != 1184) revert InvalidViewKeyLength();`.
- Audit `agreement/manager.go`:
  - `Fix M-11 defect 1`: Lower bank ID leads (`GetOrEstablish`), higher bank ID follows (`GetOrAccept`).
  - `Fix M-11 defect 2`: Resolving FIPS 203 implicit rejection pseudorandom desync via `enygma-view-key-confirm-v1:`.
  - `Fix M-11 defect 3`: Eliminating unilateral peer private seed fabrication in `LoadPeerEncapsulationKey`.
  - Field mapping in `toFieldElement`: `SHA-256("enygma-view-key-v1:" || rawSS) mod curveP`.
- Verify upstream test suite: `9/9 PASS` in `enygma_payments/go_client/agreement`.

### Phase 3: Controlled Cryptographic Benchmarking ($N=500$)
- Write [scripts/run_pq_benchmark.py](scripts/run_pq_benchmark.py) and a standalone Go benchmark runner using `filippo.io/mlkem768` vs `crypto/ecdh` (X25519) and `crypto/elliptic` (P-256 / secp256k1).
- Benchmark:
  - Key Generation latency (median, p95, cold start).
  - Encapsulation / Shared Secret derivation latency.
  - Decapsulation latency.
  - Payload sizes: `1,184 B` public key vs `32 B` / `64 B`; `1,088 B` ciphertext vs `32 B`.
  - Memory allocation overhead per operation.
  - Baby Jubjub field reduction latency (`big.Int.Mod`).
- Save output to [data/mlkem768_vs_classical_benchmark.json](data/mlkem768_vs_classical_benchmark.json).

### Phase 4: Foundry Invariant Prototype & Forensic Testbench
- Develop [contracts/PQAccountRegistry.sol](contracts/PQAccountRegistry.sol):
  - Label: *"Architectural Prototype & Illustrative Invariant Testbench"*.
  - Implements `registerAccount` with strict `1,184 B` view-key validation.
  - Implements Guard-ON vs Guard-OFF toggles:
    - `enforceKeyLength`: rejects non-1184 byte keys with `InvalidViewKeyLength`.
    - `enforceConfirmationHash`: rejects mismatched confirmation tags with `ConfirmationTagMismatch`.
    - `enforcePeerOrdering`: rejects improper leader/follower registration with `UnauthorizedLeaderDirection`.
- Develop [test/PQInvariantAudit.t.sol](test/PQInvariantAudit.t.sol) (`8/8 PASS`, `256` fuzz runs):
  - Test valid ML-KEM-768 registration.
  - Test rejection of truncated (32 B, 64 B classical) keys when Guard ON.
  - Test confirmation tag verification and replay prevention.
  - Test state-machine invariant bounds under fuzzing.
- Develop [test/PQMainnetFork.t.sol](test/PQMainnetFork.t.sol) (`3/3 PASS`):
  - Fork live Rayls Public Chain (`Chain ID 72957`).
  - Measure gas consumption of registering an 1,184-byte encapsulation key on live chain state.

### Phase 5: Live Mainnet 72957 Cadence & Calldata Telemetry
- Run [scripts/mainnet_pq_telemetry.py](scripts/mainnet_pq_telemetry.py) against `https://mainnet-rpc.rayls.com`.
- Sample 1,000 consecutive blocks (#14,350,000+), verifying unbroken parent hash links, block time variance, gas price (48 Gwei), and block gas ceiling (500M).
- Calculate exact on-chain calldata gas costs for `1,184 B` zero vs non-zero bytes (EIP-2028: 16 gas per non-zero byte).
- Save to [data/rayls_mainnet_pq_telemetry.json](data/rayls_mainnet_pq_telemetry.json).

### Phase 6: High-Contrast Visual Assets (Signature Light Gradient)
- Generate 4 visual assets using Python Pillow with full-bleed `#B49AFF -> #ECFB3E` gradient:
  1. [assets/cover_image_post_quantum.png](assets/cover_image_post_quantum.png) - Header cover image.
  2. [assets/diagram_1_hndl_threat_model.png](assets/diagram_1_hndl_threat_model.png) - Harvest-Now-Decrypt-Later timeline vs 30-year debt lifecycle.
  3. [assets/diagram_2_mlkem_zk_pipeline.png](assets/diagram_2_mlkem_zk_pipeline.png) - ML-KEM-768 key encapsulation + Baby Jubjub ZK field reduction pipeline.
  4. [assets/diagram_3_pq_empirical_benchmarks.png](assets/diagram_3_pq_empirical_benchmarks.png) - Empirical benchmark chart (ML-KEM-768 vs X25519 vs secp256k1).

### Phase 7: Start-to-Finish Pre-Flight & Screen-Recording Checklist
- Write [scripts/record_demo_showcase.sh](scripts/record_demo_showcase.sh) automated terminal demonstration:
  - `[0/4]` Hardware specs, toolchain versions, and pinned git SHAs.
  - `[1/4]` Live Rayls Mainnet (`72957`) RPC queries.
  - `[2/4]` Deterministic offline Foundry invariant tests (`8/8 PASS`).
  - `[3/4]` Live Mainnet fork gas execution (`3/3 PASS`).
  - `[4/4]` Upstream Go `agreement` unit tests (`9/9 PASS`) and dataset gate.
- Document Section 7 device specifications and copy-paste reproduction commands.

### Phase 8: Deliverables, Cross-Post Package & GitHub Actions CI
- Author technical monograph: [POST_QUANTUM_BANKING_HNDL_RAYLS_DEEP_DIVE.md](POST_QUANTUM_BANKING_HNDL_RAYLS_DEEP_DIVE.md).
- Author cross-post summary: [CROSS_POST_SUMMARY.md](CROSS_POST_SUMMARY.md) (8-post X thread + Discord submission).
- Author [README.md](README.md) with green CI badge.
- Build automated [.github/workflows/verify.yml](.github/workflows/verify.yml).
- Author [docs/VOICEOVER_TTS_SCRIPT.md](docs/VOICEOVER_TTS_SCRIPT.md).
