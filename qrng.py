# qrng.py
from qiskit import QuantumCircuit, Aer, execute
import random

def get_random_bits(length: int = 8) -> str:
    """Generate random bits using quantum circuit."""
    qc = QuantumCircuit(length, length)
    qc.h(range(length))  # Apply Hadamard gate to all qubits
    qc.measure(range(length), range(length))

    backend = Aer.get_backend("qasm_simulator")
    job = execute(qc, backend, shots=1)
    result = job.result()
    counts = result.get_counts()

    # Extract the random bitstring
    random_bits = list(counts.keys())[0]
    return random_bits

def get_random_int(min_val: int = 0, max_val: int = 100) -> int:
    """Generate a random integer using QRNG bits."""
    bit_length = (max_val - min_val).bit_length()
    bits = get_random_bits(bit_length)
    value = int(bits, 2)
    return min_val + (value % (max_val - min_val + 1))

def get_random_float(min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Generate a random float using QRNG."""
    bits = get_random_bits(32)
    value = int(bits, 2) / (2**32 - 1)
    return min_val + value * (max_val - min_val)
