# IRAM-091 — Experimental Cryptographic Hash Function

**Developer:** Syed Rehan

---

## 📌 Overview

**IRAM-091** is an experimental cryptographic hash function designed for educational study of hash function internals. It produces a **256-bit (64 hex characters)** output and processes data in **512-bit blocks** through **91 rounds** of compression.

> ⚠️ **EDUCATIONAL / EXPERIMENTAL ONLY — NOT FOR PRODUCTION USE**

---

## ✨ Features

| Feature | Specification |
|---------|---------------|
| **Output Size** | 256 bits (64 hex chars) |
| **Block Size** | 512 bits (64 bytes) |
| **Rounds** | 91 |
| **State Registers** | 8 × 32-bit (A–H) |
| **Construction** | Merkle-Damgård with Davies-Meyer feedforward |
| **Padding** | Custom 0xAB marker + 64-bit length |
| **Inspiration** | SHA-256 (high-level structure only) |

---

## 🔍 How It Works

```

Input Message (any length)
↓
Padding (0xAB marker + zeros + 64-bit length)
↓
Initialize 8 registers (A–H) with IVs
↓
For each 512-bit block:
├── Expand 16 words → 91-word schedule (W[])
├── Save state for feedforward
├── 91 rounds of compression with F1–F4, K[], W[]
└── Feedforward: state += original state
↓
Concatenate A||B||C||D||E||F||G||H
↓
Output: 256-bit digest

```

---

## 🧬 Core Components

### Initialization Vectors (IVs)

Derived from transcendental constants (e, φ, √3, √5, ln 2, π²/6, ∛2, γ):

| Register | Value |
|----------|-------|
| IV[0] | 0xB7E15162 |
| IV[1] | 0x9E3779B9 |
| IV[2] | 0xBB67AE85 |
| IV[3] | 0x3C6EF372 |
| IV[4] | 0xB17217F7 |
| IV[5] | 0xA51A6625 |
| IV[6] | 0x428A2F98 |
| IV[7] | 0x93C467E3 |

### Nonlinear Functions (F1–F4)

| Function | Formula |
|----------|---------|
| **F1** | `(x AND y) XOR (NOT x AND z) XOR (y AND NOT z)` |
| **F2** | `(ROTR(x,7) AND y) XOR (ROTL(x,11) AND NOT y) XOR z` |
| **F3** | `ROTR(x,3) XOR ROTL(y,13) XOR ROTR(z,17)` |
| **F4** | `(x XOR y XOR z) OR (ROTR(x,5) AND ROTL(z,9))` |

### State Sigma Functions

| Function | Formula |
|----------|---------|
| **Γ0(x)** | `ROTR(x,2) XOR ROTL(x,13) XOR ROTR(x,22)` |
| **Γ1(x)** | `ROTR(x,5) XOR ROTL(x,15) XOR ROTR(x,29)` |

### Schedule Sigma Functions

| Function | Formula |
|----------|---------|
| **Σ0(x)** | `ROTR(x,6) XOR ROTR(x,18) XOR SHR(x,3)` |
| **Σ1(x)** | `ROTR(x,11) XOR ROTR(x,25) XOR SHR(x,10)` |

---

## 📊 Round Constants (K[0..90])

Constants derived from cube roots of the first 91 primes:

```

K[0] = 0x428A2F98 (p=2)
K[1] = 0x71374491 (p=3)
K[2] = 0xB5C0FBCF (p=5)
...
K[90] = 0xC226A69A (p=467)

```

---

## 📥 Test Vectors

| Input | IRAM-091 Digest |
|-------|-----------------|
| *(empty string)* | `21bd903d33ddc0bc921b6b0eb2f9993705eabcc740287d2eb0b24b81ee9f4b35` |
| `"a"` | `4660c1228358e8edeba97002bab9e00d8db5a287df6e477bf1987ff322f82ad5` |
| `"hello"` | `c4594fdaa2bacdc4a0190a8fdcd74266ebdeeddde537f7b31d7242fcd284ca58` |
| `"Hello"` | `8da7d710bb9a7390746e547e5373a2d56438742a0682a9384088fa1b6e774680` |
| `"IRAM-091"` | `a5e634f7814c65ee410f7831676e8f32a8126463ab2f535cdc240d8e3f809f6d` |
| `"The quick brown fox jumps over the lazy dog"` | `00ef5118c803781cd4ae4e66d6923fcb9b074c3dc90f2bddbbb703ae8ae95c87` |

---

## 🌊 Avalanche Effect

A single-bit change ("hello" → "Hello") results in **145/256 bits (56.6%)** flipping — close to the ideal 50%.

| Metric | IRAM-091 | Ideal |
|--------|----------|-------|
| Bit difference | 56.6% | ~50% |
| Status | ✅ GOOD | — |

---

## 🔐 Security Analysis

| Property | Status | Notes |
|----------|--------|-------|
| Collision Resistance | ⚠️ UNVERIFIED | 2¹²⁸ theoretical bound |
| Preimage Resistance | ⚠️ UNVERIFIED | 2²⁵⁶ theoretical bound |
| Diffusion | ✅ GOOD | 56.6% avalanche |
| Confusion | ✅ PRESENT | F1–F4 nonlinearity |
| Length Extension | ❌ VULNERABLE | Use HMAC wrapper |
| Algebraic Attacks | ⚠️ UNANALYZED | No GF(2) analysis done |

> ⚠️ **IRAM-091 has NOT been publicly cryptanalyzed. Do not use for real security.**

---

## 🛠️ Technical Stack

| Component | Technology |
|-----------|------------|
| Frontend | HTML5, CSS3, JavaScript |
| Fonts | Orbitron, Share Tech Mono, Rajdhani |
| Hash Implementation | Pure JavaScript (WebAssembly not required) |
| Styling | Tailwind CSS (CDN) + Custom CSS |

---

## 📁 Project Structure

```

iram091-website/
├── index.html          # Complete specification + live demo
├── assets/
│   └── (none required)
└── README.md           # This file

```

---

## 🚀 Running Locally

```bash
# 1. Save the HTML file
nano index.html

# 2. Open in browser
open index.html  # macOS
# OR
xdg-open index.html  # Linux
# OR
start index.html  # Windows
```

No server required — pure client-side JavaScript.

---

🎮 Interactive Demo Features

Feature Description
Live Hash Calculator Type any text → instant IRAM-091 hash
Avalanche Comparator Compare two inputs side-by-side
Bit Difference Meter Visual percentage of differing bits
K-Table Viewer All 91 round constants displayed
Test Vectors Verified against reference implementation

---

🔧 JavaScript Implementation Details

The browser-based implementation includes:

```javascript
// Core functions
rotr(x, n)    // Rotate right
rotl(x, n)    // Rotate left
add32(...)    // Modular 32-bit addition

// Hash pipeline
pad(msgBytes)         // 0xAB + zeros + 64-bit length
expandSchedule(block) // 16 → 91 words
compress(state, block)// 91 rounds with F1–F4
iram091(input)        // Main entry point
```

---

📊 Comparison with SHA-256

Feature SHA-256 IRAM-091
Rounds 64 91
Padding marker 0x80 0xAB
Constants source ∛prime (1st 64) ∛prime (1st 91)
IV source √prime e, φ, √3, √5, ln2, π²/6, ∛2, γ
Schedule terms 4 back-references 5 back-references
Round temps T1, T2 T1, T2, T3
Rotations mix Only ROTR ROTR + ROTL

---

⚠️ Disclaimer

IRAM-091 is an EXPERIMENTAL cryptographic hash function created for educational purposes.

· ❌ NOT reviewed by cryptographers
· ❌ NOT safe for production use
· ❌ NOT a replacement for SHA-256 / SHA-3
· ✅ Educational demonstration only
· ✅ Learn how hash functions work
· ✅ Study avalanche effect and diffusion

---

👨‍💻 Developer

Syed Rehan

---

📄 License

Educational use only. Not for production or security-critical applications.

---

🔗 Live Demo

The complete specification is available as a single HTML file with:

· Full algorithm documentation
· Interactive hash calculator
· Avalanche effect visualizer
· All 91 round constants

---

📝 Acknowledgments

· SHA-256 for high-level structural inspiration
· NIST for cryptographic hash function education
· Open source cryptography community

---

For educational exploration of hash functions.

---

📋 Pseudocode Reference

```python
def IRAM091(message):
    # Padding
    bits = len(message) * 8
    message += b'\xAB'
    while len(message) % 64 != 56:
        message += b'\x00'
    message += bits.to_bytes(8, 'big')
    
    # Initialize state
    state = IVs
    
    # Process blocks
    for block in blocks(message, 64):
        W = expand_schedule(block)
        original = state.copy()
        
        for i in range(91):
            T1 = H + Γ1(E) + F2(E,F,G) + K[i] + W[i]
            T2 = Γ0(A) + F1(A,B,C)
            T3 = F3(B,D,F) ^ F4(A,C,E)
            
            H, G, F = G, F, E
            E = D + T1
            D, C, B = C, B, A
            A = T1 + T2 + T3
        
        # Feedforward
        state = [state[j] + original[j] for j in range(8)]
    
    return concat(state)
```

---

⚠️ Remember: This is an educational experiment, not a production cryptographic primitive.
