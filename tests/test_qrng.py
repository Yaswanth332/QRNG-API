from qrng import sample_random_bits, random_hex


def test_sample_random_bits_length():
    bits = sample_random_bits(16)
    assert len(bits) == 16
    assert all(b in (0, 1) for b in bits)


def test_random_hex_length():
    h = random_hex(8)
    assert isinstance(h, str)
    assert len(h) == 16
