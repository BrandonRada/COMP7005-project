import socket
import argparse
import sys

from common import decode_packet, encode_ack
from logger import make_logger

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--listen-ip", required=True)
    parser.add_argument("--listen-port", type=int, required=True)
    args = parser.parse_args()

    log = make_logger("server.log")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except OSError as e:
        log(f"ERROR: could not create socket: {e}")
        sys.exit(1)

    try:
        sock.bind((args.listen_ip, args.listen_port))
    except OSError as e:
        log(f"ERROR: Could not bind to {args.listen_ip}:{args.listen_port}: {e}")
        sys.exit(1)

    log(f"Server listening on {args.listen_ip}:{args.listen_port}")

    #
    while True:
        try:
            data, addr = sock.recvfrom(4096)
        except KeyboardInterrupt:
            break
        except Exception as e:
            log(f"Recv error: {e}")
            continue

        try:
            pkt = decode_packet(data)
        except Exception as e:
            log(f"Failed to decode packet from {addr}: {e}")
            continue

        seq = pkt["seq"]
        payload = pkt["payload"]

        log(f"RECEIVED from {addr} | seq={seq} payload={payload!r}")

        # Print message content (decoded as UTF-8 if it's text)
        try:
            print(payload.decode("utf-8"))
        except Exception:
            print(payload)

        # Send ACK
        try:
            ack_packet = encode_ack(seq)
            sock.sendto(ack_packet, addr)
            log(f"SENT ACK to {addr} | ack={seq}")
        except Exception as e:
            log(f"Error sending ACK to {addr}: {e}")

    print("\nClosing socket...")
    sock.close()
    log("Server stopped cleanly.")

if __name__ == "__main__":
    main()
