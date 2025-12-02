import json
import struct
import sys
import signal

PACKET_FORMAT = "!IIH"
HEADER_SIZE = struct.calcsize(PACKET_FORMAT)

FLAG_ACK = 1  # ACK flag

def encode_packet(seq: int, ack: int, flags: int, payload: bytes) -> bytes:
    """Encode a packet into bytes."""
    header = struct.pack(PACKET_FORMAT, seq, ack, flags)
    return header + payload

def decode_packet(data: bytes) -> dict:
    """Decode bytes into a packet."""
    if len(data) < HEADER_SIZE:
        raise ValueError("Packet too short")

    header = data[:HEADER_SIZE]
    payload = data[HEADER_SIZE:]

    seq, ack, flags = struct.unpack(PACKET_FORMAT, header)

    return {
        "seq": seq,
        "ack": ack,
        "flags": flags,
        "payload": payload,
    }

def encode_ack(seq: int) -> bytes:
    """Create an ACK packet."""
    return encode_packet(seq=0, ack=seq, flags=FLAG_ACK, payload=b"")

