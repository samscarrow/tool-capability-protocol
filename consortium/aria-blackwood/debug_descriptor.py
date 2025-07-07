#!/usr/bin/env python3
"""Debug descriptor creation to fix size issue"""

import hashlib
import secrets
import struct
import time

def debug_descriptor_creation():
    """Debug the quantum descriptor creation process"""
    
    print("Debugging quantum descriptor creation...")
    
    # 1. Magic: TCP\x03 (4 bytes)
    magic = b'TCP\x03'
    print(f"Magic: {len(magic)} bytes")
    
    # 2. Command hash: SHAKE-256 (4 bytes)
    shake = hashlib.shake_256()
    shake.update(b"cat file.txt")
    command_hash = shake.digest(4)
    print(f"Command hash: {len(command_hash)} bytes")
    
    # 3. Security flags (4 bytes)
    flags_bytes = struct.pack('>I', 0)
    print(f"Security flags: {len(flags_bytes)} bytes")
    
    # 4. Quantum signature (8 bytes)
    quantum_signature = secrets.token_bytes(8)
    print(f"Quantum signature: {len(quantum_signature)} bytes")
    
    # 5. Performance data (6 bytes) - 3 x 2-byte values
    performance = struct.pack('>HHH', 1000, 1024, 512)
    print(f"Performance data: {len(performance)} bytes")
    
    # 6. Quantum level (2 bytes)
    quantum_level_bytes = struct.pack('>H', 32768)
    print(f"Quantum level: {len(quantum_level_bytes)} bytes")
    
    # 7. Timestamp (2 bytes)
    timestamp_bytes = struct.pack('>H', int(time.time() // 60) & 0xFFFF)
    print(f"Timestamp: {len(timestamp_bytes)} bytes")
    
    # Calculate total without CRC
    descriptor_without_crc = (
        magic + command_hash + flags_bytes + quantum_signature +
        performance + quantum_level_bytes + timestamp_bytes
    )
    
    print(f"\nDescriptor without CRC: {len(descriptor_without_crc)} bytes")
    print("Breakdown:")
    print(f"  Magic (4) + Hash (4) + Flags (4) + Signature (8) + Performance (6) + Level (2) + Timestamp (2) = {4+4+4+8+6+2+2}")
    
    # 8. CRC32 (4 bytes)
    import zlib
    crc32 = zlib.crc32(descriptor_without_crc) & 0xffffffff
    crc32_bytes = struct.pack('>I', crc32)
    print(f"CRC32: {len(crc32_bytes)} bytes")
    
    # Final descriptor
    final_descriptor = descriptor_without_crc + crc32_bytes
    print(f"\nFinal descriptor: {len(final_descriptor)} bytes")
    
    if len(final_descriptor) == 32:
        print("✅ Correct size!")
    else:
        print(f"❌ Wrong size! Expected 32, got {len(final_descriptor)}")
        
        # Let's see where the extra bytes are coming from
        print("\nDetailed byte analysis:")
        offset = 0
        for component, size in [("Magic", 4), ("Hash", 4), ("Flags", 4), ("Signature", 8), ("Performance", 6), ("Level", 2), ("Timestamp", 2), ("CRC", 4)]:
            if offset + size <= len(final_descriptor):
                actual_bytes = final_descriptor[offset:offset+size]
                print(f"  {component}: {size} bytes -> {actual_bytes.hex()}")
                offset += size
            else:
                print(f"  {component}: Expected {size} bytes but only {len(final_descriptor) - offset} remaining")
        
        print(f"\nTotal expected: 32 bytes")
        print(f"Total actual: {len(final_descriptor)} bytes")

if __name__ == "__main__":
    debug_descriptor_creation()