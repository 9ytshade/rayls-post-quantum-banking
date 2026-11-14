# Voiceover Script: Week 8 Post-Quantum Banking & HNDL Protocol Demonstration

> **Target Video Length:** ~50-60 seconds  
> **Script Word Count:** ~150 words  
> **Target Tool:** ElevenLabs / Any Neural TTS Generator (Paced, confident, authoritative technical tone)  
> **Governing Script:** `bash scripts/record_demo_showcase.sh` (or modular `bash scripts/run_research_stage.sh [1-6|all]`)  

---

## 🎬 Part 1: Timestamped Cue Sheet & Screen-Recording Alignment

| Timestamp | Visual Terminal Cue (What Appears on Screen) | Voiceover Narration |
| :---: | :--- | :--- |
| **00:00 - 00:08** | `[STAGE 1/6] HARDWARE, TOOLCHAIN & REPOSITORY COMMIT PRE-FLIGHT` - Host kernel, CPU model (i3-3110M @ 2.40 GHz), RAM, Go, Forge, Solc, and pinned Enygma commit `@ a9b06c00`. | "To examine post-quantum security on Rayls, I begin with an automated pre-flight audit verifying my machine hardware, toolchains, and pinned upstream Enygma source code." |
| **00:08 - 00:17** | `[STAGE 2/6] UPSTREAM ENYGMA SOURCE CODE FORENSICS & INVARIANT AUDIT` - Enygma.sol line 532 key length check, Fix M-11 defect 1 (leader election), defect 2 (confirmation hash), and Baby Jubjub field reduction. | "Inspecting upstream contracts and client source code reveals strict 1,184-byte view key enforcement and explicit defense against implicit rejection desync." |
| **00:17 - 00:25** | `[STAGE 3/6] LIVE RAYLS PUBLIC CHAIN MAINNET (CHAIN ID 72957) REAL-TIME TELEMETRY` - Tip block #14,551,000+, 0-block lag, 57.60 Gwei gas price, 21,930-byte ConsensusRegistry bytecode. | "Next, I query live Rayls Mainnet on Chain 72957, confirming zero-block finalized lag, baseline gas prices, and deployed consensus contracts." |
| **00:25 - 00:34** | `[STAGE 4/6] LIVE POST-QUANTUM VS CLASSICAL CRYPTOGRAPHIC BENCHMARKS` - Live execution of benchmark_pq.go: ML-KEM-768 encap 257 us vs X25519 350.9 us (26.8% faster). | "Running cryptographic benchmarks shows ML-KEM-768 encapsulation executing in 257 microseconds, outperforming classical X25519 by 26.8 percent." |
| **00:34 - 00:43** | `[STAGE 5/6] OFFLINE DETERMINISTIC FOUNDRY INVARIANT AUDIT (8/8 PASS)` - 8 tests pass including 256 fuzz runs, demonstrating CRIT-PQ1 through CRIT-PQ4. | "In Foundry, eight invariant tests pass across 256 fuzz runs, proving that malformed classical keys revert and counterparty liveness is preserved." |
| **00:43 - 00:54** | `[STAGE 6/6] LIVE MAINNET FORK GAS EXECUTION & UPSTREAM INTEGRITY SUITE` - Fork gas 308,164 gas, 9/9 upstream Go agreement unit passes, verify_datasets.py exit 0. | "Finally, live Mainnet fork execution confirms view key registration costs 308,164 gas, while upstream unit tests and dataset gates pass cleanly." |

---

## 🎙️ Part 2: Pure Voiceover Text (Copy & Paste for TTS Generation)

```text
To examine post-quantum security on Rayls, I begin with an automated pre-flight audit verifying my machine hardware, toolchains, and pinned upstream Enygma source code.

Inspecting upstream contracts and client source code reveals strict 1,184-byte view key enforcement and explicit defense against implicit rejection desync.

Next, I query live Rayls Mainnet on Chain 72957, confirming zero-block finalized lag, baseline gas prices, and deployed consensus contracts.

Running cryptographic benchmarks shows ML-KEM-768 encapsulation executing in 257 microseconds, outperforming classical X25519 by 26.8 percent.

In Foundry, eight invariant tests pass across 256 fuzz runs, proving that malformed classical keys revert and counterparty liveness is preserved.

Finally, live Mainnet fork execution confirms view key registration costs 308,164 gas, while upstream unit tests and dataset gates pass cleanly.
```
