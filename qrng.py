# qrng.py
"""
QRNG helper: try to use Qiskit/Aer when available, otherwise fall back
to a secure pseudo-random generator (secrets).
"""

# Attempt Qiskit imports, but tolerate missing Aer or Qiskit entirely
QuantumCircuit = None
Aer = None
execute = None

try:
    from qiskit import QuantumCircuit, execute  # type: ignore
    try:
        # Aer may live under qiskit or qiskit.providers.aer depending on install
        from qiskit import Aer  # type: ignore
    except Exception:
        try:
            from qiskit.providers.aer import Aer  # type: ignore
        except Exception:
            Aer = None
except Exception:
    # Qiskit not available
    QuantumCircuit = None
    Aer = None
    execute = None

import secrets
from typing import List


def _aer_available() -> bool:
    return QuantumCircuit is not None and Aer is not None and execute is not None


def get_random_bits(length: int = 8) -> str:
    """Return a random bitstring of `length` bits.

    Uses a Qiskit Aer simulator when available; otherwise falls back to
    Python's `secrets` for cryptographically secure pseudo-random bits.
    """
    if _aer_available():
        try:
            qc = QuantumCircuit(length, length)
            qc.h(range(length))
            qc.measure(range(length), range(length))

            # Try commonly available backend names
            backend = None
            try:
                backend = Aer.get_backend("aer_simulator")
            except Exception:
                try:
                    backend = Aer.get_backend("qasm_simulator")
                except Exception:
                    backend = None

            if backend is not None:
                job = execute(qc, backend, shots=1)
                result = job.result()
                counts = result.get_counts()
                # counts keys are bitstrings (big-endian), take the first
                random_bits = list(counts.keys())[0]
                # ensure returned string length matches requested length
                return random_bits.zfill(length)
        except Exception:
            # if any Qiskit runtime error occurs, fall back to secrets
            pass

    # Fallback: use secrets to generate cryptographically secure bits
    n = secrets.randbits(length)
    return format(n, 'b').zfill(length)


def get_random_int(min_val: int = 0, max_val: int = 100) -> int:
    """Generate a random integer within [min_val, max_val] using QRNG bits or fallback."""
    if min_val > max_val:
        raise ValueError("min_val must be <= max_val")
    span = max_val - min_val + 1
    bit_length = span.bit_length()

    # rejection sampling to avoid modulo bias
    while True:
        bits = get_random_bits(bit_length)
        value = int(bits, 2)
        if value < (1 << bit_length) - ((1 << bit_length) % span):
            return min_val + (value % span)


def get_random_float(min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Generate a random float in [min_val, max_val] using 32 bits of randomness."""
    bits = get_random_bits(32)
    value = int(bits, 2) / (2**32 - 1)
    return min_val + value * (max_val - min_val)
