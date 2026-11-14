package main

import (
	"crypto/ecdh"
	"crypto/rand"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"math/big"
	"os"
	"runtime"
	"sort"
	"time"

	"filippo.io/mlkem768"
)

var curveP, _ = new(big.Int).SetString(
	"2736030358979909402780800718157159386076813972158567259200215660948447373041", 10)

type LatencyStats struct {
	Count         int     `json:"count"`
	ColdFirstUs   float64 `json:"cold_first_us"`
	WarmMedianUs  float64 `json:"warm_median_us"`
	WarmMeanUs    float64 `json:"warm_mean_us"`
	WarmP95Us     float64 `json:"warm_p95_us"`
	WarmMinUs     float64 `json:"warm_min_us"`
	WarmMaxUs     float64 `json:"warm_max_us"`
}

type PrimitiveBenchmark struct {
	Name            string       `json:"name"`
	Standard        string       `json:"standard"`
	SecurityLevel   string       `json:"security_level"`
	PublicKeyBytes  int          `json:"public_key_bytes"`
	CiphertextBytes int          `json:"ciphertext_bytes"`
	SharedSecretBytes int        `json:"shared_secret_bytes"`
	KeygenLatency   LatencyStats `json:"keygen_latency"`
	EncapLatency    LatencyStats `json:"encap_latency"`
	DecapLatency    LatencyStats `json:"decap_latency"`
	AllocBytesPerOp int64        `json:"alloc_bytes_per_op"`
}

type BenchmarkReport struct {
	Timestamp          string               `json:"timestamp"`
	Environment        string               `json:"environment"`
	CPUModel           string               `json:"cpu_model"`
	LogicalCPUs        int                  `json:"logical_cpus"`
	GoVersion          string               `json:"go_version"`
	SampleCountN       int                  `json:"sample_count_n"`
	Primitives         []PrimitiveBenchmark `json:"primitives"`
	BabyJubjubReduction LatencyStats       `json:"baby_jubjub_reduction_latency"`
	ConfirmationIDHash  LatencyStats       `json:"confirmation_id_hash_latency"`
}

func computeStats(samples []time.Duration) LatencyStats {
	if len(samples) == 0 {
		return LatencyStats{}
	}
	cold := float64(samples[0].Nanoseconds()) / 1000.0

	warm := make([]float64, len(samples)-1)
	var sum float64
	for i := 1; i < len(samples); i++ {
		us := float64(samples[i].Nanoseconds()) / 1000.0
		warm[i-1] = us
		sum += us
	}
	sort.Float64s(warm)

	median := warm[len(warm)/2]
	mean := sum / float64(len(warm))
	p95Idx := int(float64(len(warm)) * 0.95)
	if p95Idx >= len(warm) {
		p95Idx = len(warm) - 1
	}
	p95 := warm[p95Idx]
	min := warm[0]
	max := warm[len(warm)-1]

	return LatencyStats{
		Count:        len(samples),
		ColdFirstUs:  cold,
		WarmMedianUs: median,
		WarmMeanUs:   mean,
		WarmP95Us:    p95,
		WarmMinUs:    min,
		WarmMaxUs:    max,
	}
}

func toFieldElement(rawSS []byte) *big.Int {
	h := sha256.Sum256(append([]byte("enygma-view-key-v1:"), rawSS...))
	n := new(big.Int).SetBytes(h[:])
	return n.Mod(n, curveP)
}

func confirmationID(rawSS []byte) []byte {
	h := sha256.Sum256(append([]byte("enygma-view-key-confirm-v1:"), rawSS...))
	return h[:]
}

func main() {
	N := 500
	fmt.Printf("Running Post-Quantum vs Classical KEM Benchmark (N=%d)...\n", N)

	// 1. Benchmark ML-KEM-768
	keygenSamplesMLKEM := make([]time.Duration, N)
	encapSamplesMLKEM := make([]time.Duration, N)
	decapSamplesMLKEM := make([]time.Duration, N)

	var m0, m1 runtime.MemStats
	runtime.GC()
	runtime.ReadMemStats(&m0)

	var lastDK *mlkem768.DecapsulationKey
	var lastEK []byte
	var lastCT []byte

	for i := 0; i < N; i++ {
		t0 := time.Now()
		dk, err := mlkem768.GenerateKey()
		if err != nil {
			panic(err)
		}
		keygenSamplesMLKEM[i] = time.Since(t0)
		lastDK = dk
		lastEK = dk.EncapsulationKey()

		t1 := time.Now()
		ct, ss1, err := mlkem768.Encapsulate(lastEK)
		if err != nil {
			panic(err)
		}
		encapSamplesMLKEM[i] = time.Since(t1)
		lastCT = ct

		t2 := time.Now()
		ss2, err := mlkem768.Decapsulate(lastDK, lastCT)
		if err != nil {
			panic(err)
		}
		decapSamplesMLKEM[i] = time.Since(t2)

		if string(ss1) != string(ss2) {
			panic("ML-KEM-768 shared secret mismatch!")
		}
	}
	runtime.ReadMemStats(&m1)
	allocMLKEM := int64(m1.TotalAlloc-m0.TotalAlloc) / int64(N)

	// 2. Benchmark Classical X25519
	keygenSamplesX25519 := make([]time.Duration, N)
	encapSamplesX25519 := make([]time.Duration, N)
	decapSamplesX25519 := make([]time.Duration, N)

	runtime.GC()
	runtime.ReadMemStats(&m0)
	curve25519 := ecdh.X25519()

	for i := 0; i < N; i++ {
		t0 := time.Now()
		privA, err := curve25519.GenerateKey(rand.Reader)
		if err != nil {
			panic(err)
		}
		keygenSamplesX25519[i] = time.Since(t0)
		pubA := privA.PublicKey()

		// Bob generates ephemeral key and encapsulates (computes ECDH)
		t1 := time.Now()
		privB, err := curve25519.GenerateKey(rand.Reader)
		if err != nil {
			panic(err)
		}
		pubB := privB.PublicKey()
		ss1, err := privB.ECDH(pubA)
		if err != nil {
			panic(err)
		}
		encapSamplesX25519[i] = time.Since(t1)

		// Alice decapsulates using Bob's ephemeral public key
		t2 := time.Now()
		ss2, err := privA.ECDH(pubB)
		if err != nil {
			panic(err)
		}
		decapSamplesX25519[i] = time.Since(t2)

		if string(ss1) != string(ss2) {
			panic("X25519 shared secret mismatch!")
		}
	}
	runtime.ReadMemStats(&m1)
	allocX25519 := int64(m1.TotalAlloc-m0.TotalAlloc) / int64(N)

	// 3. Benchmark Classical P-256 (NIST secp256r1)
	keygenSamplesP256 := make([]time.Duration, N)
	encapSamplesP256 := make([]time.Duration, N)
	decapSamplesP256 := make([]time.Duration, N)

	runtime.GC()
	runtime.ReadMemStats(&m0)
	curveP256 := ecdh.P256()

	for i := 0; i < N; i++ {
		t0 := time.Now()
		privA, err := curveP256.GenerateKey(rand.Reader)
		if err != nil {
			panic(err)
		}
		keygenSamplesP256[i] = time.Since(t0)
		pubA := privA.PublicKey()

		t1 := time.Now()
		privB, err := curveP256.GenerateKey(rand.Reader)
		if err != nil {
			panic(err)
		}
		pubB := privB.PublicKey()
		ss1, err := privB.ECDH(pubA)
		if err != nil {
			panic(err)
		}
		encapSamplesP256[i] = time.Since(t1)

		t2 := time.Now()
		ss2, err := privA.ECDH(pubB)
		if err != nil {
			panic(err)
		}
		decapSamplesP256[i] = time.Since(t2)

		if string(ss1) != string(ss2) {
			panic("P-256 shared secret mismatch!")
		}
	}
	runtime.ReadMemStats(&m1)
	allocP256 := int64(m1.TotalAlloc-m0.TotalAlloc) / int64(N)

	// 4. Benchmark Baby Jubjub Field Reduction & Confirmation ID
	reductionSamples := make([]time.Duration, N)
	confirmIDSamples := make([]time.Duration, N)
	rawSampleKey := make([]byte, 32)
	rand.Read(rawSampleKey)

	for i := 0; i < N; i++ {
		t0 := time.Now()
		fe := toFieldElement(rawSampleKey)
		reductionSamples[i] = time.Since(t0)
		_ = fe

		t1 := time.Now()
		cid := confirmationID(rawSampleKey)
		confirmIDSamples[i] = time.Since(t1)
		_ = cid
	}

	report := BenchmarkReport{
		Timestamp:    time.Now().UTC().Format(time.RFC3339),
		Environment:  "WSL2 Ubuntu 24.04 LTS (x86_64)",
		CPUModel:     "Intel(R) Core(TM) i3-3110M CPU @ 2.40GHz",
		LogicalCPUs:  runtime.NumCPU(),
		GoVersion:    runtime.Version(),
		SampleCountN: N,
		Primitives: []PrimitiveBenchmark{
			{
				Name:              "ML-KEM-768",
				Standard:          "NIST FIPS 203 (Post-Quantum Lattice Module-LWE)",
				SecurityLevel:     "NIST Security Category 3 (128-bit quantum, >= AES-192 equivalent)",
				PublicKeyBytes:    1184,
				CiphertextBytes:   1088,
				SharedSecretBytes: 32,
				KeygenLatency:     computeStats(keygenSamplesMLKEM),
				EncapLatency:      computeStats(encapSamplesMLKEM),
				DecapLatency:      computeStats(decapSamplesMLKEM),
				AllocBytesPerOp:   allocMLKEM,
			},
			{
				Name:              "X25519",
				Standard:          "RFC 7748 (Classical Montgomery Curve Diffie-Hellman)",
				SecurityLevel:     "128-bit Classical (0-bit Quantum against Shor's Algorithm)",
				PublicKeyBytes:    32,
				CiphertextBytes:   32, // Ephemeral public key
				SharedSecretBytes: 32,
				KeygenLatency:     computeStats(keygenSamplesX25519),
				EncapLatency:      computeStats(encapSamplesX25519),
				DecapLatency:      computeStats(decapSamplesX25519),
				AllocBytesPerOp:   allocX25519,
			},
			{
				Name:              "P-256 (secp256r1)",
				Standard:          "NIST SP 800-186 / FIPS 186-4 (Classical Weierstrass Curve)",
				SecurityLevel:     "128-bit Classical (0-bit Quantum against Shor's Algorithm)",
				PublicKeyBytes:    65, // Uncompressed point
				CiphertextBytes:   65, // Ephemeral public key
				SharedSecretBytes: 32,
				KeygenLatency:     computeStats(keygenSamplesP256),
				EncapLatency:      computeStats(encapSamplesP256),
				DecapLatency:      computeStats(decapSamplesP256),
				AllocBytesPerOp:   allocP256,
			},
		},
		BabyJubjubReduction: computeStats(reductionSamples),
		ConfirmationIDHash:  computeStats(confirmIDSamples),
	}

	data, err := json.MarshalIndent(report, "", "  ")
	if err != nil {
		panic(err)
	}

	outPath := "data/mlkem768_vs_classical_benchmark.json"
	if err := os.WriteFile(outPath, data, 0644); err != nil {
		panic(err)
	}
	fmt.Printf("Benchmark complete! Saved report to %s\n", outPath)
	fmt.Printf("ML-KEM-768 Warm Median: Keygen=%.2fus, Encap=%.2fus, Decap=%.2fus | Alloc=%dB\n",
		report.Primitives[0].KeygenLatency.WarmMedianUs,
		report.Primitives[0].EncapLatency.WarmMedianUs,
		report.Primitives[0].DecapLatency.WarmMedianUs,
		report.Primitives[0].AllocBytesPerOp)
	fmt.Printf("X25519     Warm Median: Keygen=%.2fus, Encap=%.2fus, Decap=%.2fus | Alloc=%dB\n",
		report.Primitives[1].KeygenLatency.WarmMedianUs,
		report.Primitives[1].EncapLatency.WarmMedianUs,
		report.Primitives[1].DecapLatency.WarmMedianUs,
		report.Primitives[1].AllocBytesPerOp)
	fmt.Printf("BabyJubjub Reduction Median: %.2fus | Confirmation ID Hash Median: %.2fus\n",
		report.BabyJubjubReduction.WarmMedianUs,
		report.ConfirmationIDHash.WarmMedianUs)
}
