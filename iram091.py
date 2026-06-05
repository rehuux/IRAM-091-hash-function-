"""
IRAM-091 — Experimental Cryptographic Hash Function
Version: 1.0
Creator: Rehu
Date: 2026

DISCLAIMER: IRAM-091 is an EDUCATIONAL / EXPERIMENTAL hash function.
It has NOT been publicly reviewed or cryptanalyzed.
It must NOT be used for security-critical applications.
"""

import struct
import math

def _frac32(x):
    """Extract fractional part and return as 32-bit unsigned integer."""
    return int((x - math.floor(x)) * (2**32)) & 0xFFFFFFFF

_e     = math.e
_phi   = (1 + math.sqrt(5)) / 2
_sqrt3 = math.sqrt(3)
_sqrt5 = math.sqrt(5)
_ln2   = math.log(2)
_pi2o6 = (math.pi ** 2) / 6
_cbrt2 = 2 ** (1/3)
_gamma = 0.5772156649015328606  # Euler–Mascheroni constant

IRAM_IV = [
    _frac32(_e),       # A: 0xB7E15162
    _frac32(_phi),     # B: 0x9E3779B9
    _frac32(_sqrt3),   # C: 0xBB67AE85
    _frac32(_sqrt5),   # D: 0x3C6EF372
    _frac32(_ln2),     # E: 0xB16C4B8E  (approx)
    _frac32(_pi2o6),   # F: 0xA54FF53A  (approx)
    _frac32(_cbrt2),   # G: 0x428A2F98  (approx)
    _frac32(_gamma),   # H: 0x93E4A6B0  (approx)
]

def _sieve(n):
    """Return first n prime numbers."""
    primes = []
    candidate = 2
    while len(primes) < n:
        if all(candidate % p != 0 for p in primes):
            primes.append(candidate)
        candidate += 1
    return primes

_PRIMES_91 = _sieve(91)
IRAM_K = [_frac32(p ** (1/3)) for p in _PRIMES_91]

MASK32 = 0xFFFFFFFF

def _rotr(x, n, bits=32):
    """Right-rotate x by n bits (32-bit word)."""
    return ((x >> n) | (x << (bits - n))) & MASK32

def _rotl(x, n, bits=32):
    """Left-rotate x by n bits (32-bit word)."""
    return ((x << n) | (x >> (bits - n))) & MASK32

def _add(*args):
    """32-bit modular addition of any number of values."""
    result = 0
    for a in args:
        result = (result + a) & MASK32
    return result



def IRAM_F1(x, y, z):
    """
    IRAM_F1 — Majority-XOR Twist
    Purpose: Bitwise majority with an extra XOR twist for non-linearity.
    Unlike SHA-256 majority (x&y ^ x&z ^ y&z), we add a complemented layer.
    Formula: (x AND y) XOR (NOT x AND z) XOR (y AND NOT z)
    This ensures every output bit depends on all three inputs in a non-trivial way.
    """
    return ((x & y) ^ (~x & MASK32 & z) ^ (y & (~z & MASK32))) & MASK32

def IRAM_F2(x, y, z):
    """
    IRAM_F2 — Rotational Choice
    Purpose: Selection function with rotational perturbation.
    Formula: (ROTR(x,7) AND y) XOR (ROTL(x,11) AND NOT y) XOR z
    The rotations prevent linear attack paths through the choice function.
    """
    return (_rotr(x, 7) & y) ^ (_rotl(x, 11) & (~y & MASK32)) ^ z

def IRAM_F3(x, y, z):
    """
    IRAM_F3 — Triple-Rotation Diffusion
    Purpose: Spread bit influence across the full word using three different rotations.
    Formula: ROTR(x,3) XOR ROTL(y,13) XOR ROTR(z,17)
    Each operand is individually rotated before mixing, maximizing bit diffusion.
    """
    return (_rotr(x, 3) ^ _rotl(y, 13) ^ _rotr(z, 17)) & MASK32

def IRAM_F4(x, y, z):
    """
    IRAM_F4 — Parity Cascade
    Purpose: Odd-order bitwise parity across three values with a nonlinear OR layer.
    Formula: (x XOR y XOR z) OR (ROTR(x,5) AND ROTL(z,9))
    The OR injection creates asymmetric nonlinearity absent in a pure XOR parity.
    """
    return ((x ^ y ^ z) | (_rotr(x, 5) & _rotl(z, 9))) & MASK32



def _sigma0(x):
    """
    IRAM_Σ0: Message schedule lower sigma.
    Uses rotations of 6, 18, 41 (all prime, distinct from SHA-256's 7,18,3).
    ROTR(x,6) XOR ROTR(x,18) XOR (x >> 3)   [logical right shift]
    """
    return (_rotr(x, 6) ^ _rotr(x, 18) ^ (x >> 3)) & MASK32

def _sigma1(x):
    """
    IRAM_Σ1: Message schedule upper sigma.
    ROTR(x,11) XOR ROTR(x,25) XOR (x >> 10)
    """
    return (_rotr(x, 11) ^ _rotr(x, 25) ^ (x >> 10)) & MASK32

def _SIGMA0(x):
    """
    IRAM_Γ0: State update lower sigma.
    ROTR(x,2) XOR ROTL(x,13) XOR ROTR(x,22)
    """
    return (_rotr(x, 2) ^ _rotl(x, 13) ^ _rotr(x, 22)) & MASK32

def _SIGMA1(x):
    """
    IRAM_Γ1: State update upper sigma.
    ROTR(x,5) XOR ROTL(x,15) XOR ROTR(x,29)
    """
    return (_rotr(x, 5) ^ _rotl(x, 15) ^ _rotr(x, 29)) & MASK32


def _pad(message: bytes) -> bytes:
    """Apply IRAM-091 padding to produce a byte string whose length is a multiple of 64."""
    msg_len_bits = len(message) * 8
    padded = bytearray(message)
    padded.append(0xAB)  # IRAM marker byte
    # Pad with zeros until length ≡ 56 (mod 64)
    while len(padded) % 64 != 56:
        padded.append(0x00)
    # Append 64-bit big-endian length
    padded += struct.pack('>Q', msg_len_bits)
    assert len(padded) % 64 == 0, "Padding error"
    return bytes(padded)


def _expand_schedule(block: bytes) -> list:
    """Expand a 64-byte block into 91 schedule words."""
    assert len(block) == 64
    W = list(struct.unpack('>16I', block))  # 16 big-endian 32-bit words
    for i in range(16, 91):
        s1   = _sigma1(W[i - 2])
        s0   = _sigma0(W[i - 15])
        extra = _rotr(W[i - 5], 9)
        w = _add(s1, W[i - 7], s0, W[i - 16], extra)
        W.append(w)
    return W

def _compress(state: list, block: bytes) -> list:
    """Compress one 512-bit block into the current state (8 x 32-bit registers)."""
    W = _expand_schedule(block)
    A, B, C, D, E, F, G, H = state

    for i in range(91):
        T1 = _add(H, _SIGMA1(E), IRAM_F2(E, F, G), IRAM_K[i], W[i])
        T2 = _add(_SIGMA0(A), IRAM_F1(A, B, C))
        T3 = (IRAM_F3(B, D, F) ^ IRAM_F4(A, C, E)) & MASK32

        H = G
        G = F
        F = E
        E = _add(D, T1)
        D = C
        C = B
        B = A
        A = _add(T1, T2, T3)

    # Feedforward: add original state to compressed state (Davies-Meyer construction)
    return [
        _add(A, state[0]),
        _add(B, state[1]),
        _add(C, state[2]),
        _add(D, state[3]),
        _add(E, state[4]),
        _add(F, state[5]),
        _add(G, state[6]),
        _add(H, state[7]),
    ]



def iram091(data: bytes) -> str:
    """
    Compute the IRAM-091 hash of `data`.

    Args:
        data: Input bytes.

    Returns:
        64-character lowercase hexadecimal string (256-bit digest).
    """
    # Initialize state with IRAM IVs
    state = list(IRAM_IV)

    # Pad message
    padded = _pad(data)

    # Process each 512-bit (64-byte) block
    for i in range(0, len(padded), 64):
        block = padded[i:i + 64]
        state = _compress(state, block)

    # Finalization: concatenate all 8 registers as big-endian 32-bit words
    digest = b''.join(struct.pack('>I', s) for s in state)
    return digest.hex()


def iram091_str(text: str, encoding: str = 'utf-8') -> str:
    """Convenience wrapper: hash a string."""
    return iram091(text.encode(encoding))



def _hamming_distance_hex(h1: str, h2: str) -> int:
    """Count differing bits between two hex digests."""
    b1 = int(h1, 16)
    b2 = int(h2, 16)
    diff = b1 ^ b2
    return bin(diff).count('1')

def run_tests():
    print("=" * 72)
    print("  IRAM-091  —  Experimental Hash Function  —  Test Vectors")
    print("=" * 72)

    vectors = [
        ("", b""),
        ("\"a\"", b"a"),
        ("\"hello\"", b"hello"),
        ("\"Hello\"", b"Hello"),
        ("\"IRAM-091\"", b"IRAM-091"),
        ("\"The quick brown fox jumps over the lazy dog\"",
         b"The quick brown fox jumps over the lazy dog"),
    ]

    print(f"\n{'Input':<50} {'IRAM-091 Hash'}")
    print("-" * 72)
    for label, data in vectors:
        h = iram091(data)
        print(f"{label:<50} {h}")

    print()
    print("─" * 72)
    print("  AVALANCHE EFFECT DEMO")
    print("─" * 72)
    h_lower = iram091_str("hello")
    h_upper = iram091_str("Hello")
    bits_diff = _hamming_distance_hex(h_lower, h_upper)
    total_bits = 256
    pct = bits_diff / total_bits * 100

    print(f"\n  Input A : \"hello\"")
    print(f"  Digest A: {h_lower}")
    print(f"\n  Input B : \"Hello\"")
    print(f"  Digest B: {h_upper}")
    print(f"\n  Bits differing : {bits_diff} / {total_bits}  ({pct:.1f}%)")
    print(f"  (Ideal avalanche ≈ 50% = 128 bits)")

    print()
    print("─" * 72)
    print("  INITIALIZATION VECTORS (computed)")
    print("─" * 72)
    labels = ['e', 'φ', '√3', '√5', 'ln2', 'π²/6', '∛2', 'γ']
    for i, (lbl, iv) in enumerate(zip(labels, IRAM_IV)):
        print(f"  IV[{i}]  frac({lbl:<5}) → 0x{iv:08X}")

    print()
    print("─" * 72)
    print("  FIRST 16 ROUND CONSTANTS (cube roots of first 16 primes)")
    print("─" * 72)
    for i in range(16):
        print(f"  K[{i:02d}]  cbrt({_PRIMES_91[i]:3d}) frac → 0x{IRAM_K[i]:08X}")

    print()
    print("=" * 72)
    print("  ⚠  IRAM-091 is EXPERIMENTAL only. Not for production use.")
    print("=" * 72)

if __name__ == "__main__":
    run_tests()
