# qrng_api/utils.py
# Add helper functions here. For example: input validation, conversions, etc.


def bits_to_int(bits):
    return int(''.join(str(b) for b in bits), 2)
