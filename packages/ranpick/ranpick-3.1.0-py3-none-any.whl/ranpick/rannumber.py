import time
import hashlib
import math
import os
import uuid
import struct
from typing import Union, Optional

def _generate_enhanced_seed() -> int:
    """Generate cryptographically strong seed using multiple entropy sources"""
    # Hardware entropy from os.urandom (4 bytes)
    hw_entropy = struct.unpack('<I', os.urandom(4))[0]
    
    # Process and system entropy
    pid_entropy = os.getpid() & 0xFFFF
    uuid_entropy = uuid.uuid4().int & 0xFFFFFFFFFFFFFFFF
    
    # High-resolution time with nanosecond precision
    time_ns = time.time_ns()
    
    # Combine all entropy sources with bit mixing
    combined = (
        (hw_entropy << 96) |
        (pid_entropy << 80) |
        (uuid_entropy << 16) |
        (time_ns & 0xFFFF)
    )
    
    # Apply cryptographic hash for avalanche effect
    hash_input = struct.pack('<QQ', combined >> 64, combined & 0xFFFFFFFFFFFFFFFF)
    digest = hashlib.sha256(hash_input).digest()
    
    # Extract 64-bit seed from hash
    return struct.unpack('<Q', digest[:8])[0]

def _xorshift64(state: int) -> tuple[int, int]:
    """Fast, high-quality PRNG with good statistical properties"""
    state ^= state << 13
    state ^= state >> 7
    state ^= state << 17
    return state & 0xFFFFFFFFFFFFFFFF, state & 0xFFFFFFFFFFFFFFFF

def _to_float(value: int) -> float:
    """Convert 64-bit integer to float [0, 1) with maximum precision"""
    return (value >> 11) * (1.0 / (1 << 53))  # Use 53 bits for IEEE 754 double precision

def _random_from_seed(seed: int, start: float, end: float, decimal_places: int = 0) -> Union[int, float]:
    """Generate random number in range with specified precision"""
    _, random_state = _xorshift64(seed)
    normalized = _to_float(random_state)
    
    if start == 0 and end == 1 and decimal_places == 0:
        return normalized
    
    scaled = start + normalized * (end - start)
    
    if decimal_places > 0:
        multiplier = 10 ** decimal_places
        return math.floor(scaled * multiplier) / multiplier
    else:
        return int(scaled)

def rannumber(
    start: Union[int, float, str] = 0, 
    end: Union[int, float, str] = 1, 
    decimal_option: Optional[str] = None
) -> Union[int, float]:
    """Generate cryptographically strong random number"""
    # Parse string expressions
    if isinstance(start, str):
        try:
            start = eval(start)
        except Exception:
            raise ValueError(f"ranpickError: Invalid start expression: {start}.")
    if isinstance(end, str):
        try:
            end = eval(end)
        except Exception:
            raise ValueError(f"ranpickError: Invalid end expression: {end}.")

    # Parse decimal places
    decimal_places = 0
    if decimal_option and decimal_option.startswith("d"):
        try:
            decimal_places = int(decimal_option[1:])
            if decimal_places < 0 or decimal_places > 20:
                raise ValueError(f"ranpickError: Decimal places must be between 0 and 20.")
        except ValueError as e:
            if "ranpickError" in str(e):
                raise e
            raise ValueError(f"ranpickError: Invalid decimal option format: {decimal_option}.")

    # Validate range
    if start >= end:
        raise ValueError("ranpickError: Start value must be less than end value.")

    # Generate random number
    seed = _generate_enhanced_seed()
    return _random_from_seed(seed, start, end, decimal_places)