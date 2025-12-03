import socket
import sys
import argparse
import threading

from common import encode_packet, decode_packet, FLAG_ACK
from logger import make_logger
from plot_logs import plot_client_graph

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-ip", required=True)
    parser.add_argument("--target-port", type=int, required=True)
    parser.add_argument("--timeout", type=float, required=True)
    parser.add_argument("--max-retries", type=int, required=True)
    args = parser.parse_args()

    log = make_logger("client.log")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(args.timeout)
    except OSError as e:
        log(f"ERROR: could not create socket: {e}")
        sys.exit(1)

    log(f"Client sending to {args.target_ip}:{args.target_port}")

    seq = 1
    try:

        for line in sys.stdin:
            payload = line.strip("\n").encode()
            retries = 0

            while retries <= args.max_retries:
                packet = encode_packet(seq, 0, 0, payload)

                try:
                    sock.sendto(packet, (args.target_ip, args.target_port))
                    log(f"SENT | seq={seq} retries={retries} payload={payload!r}")
                except OSError as e:
                    log(f"Send error: {e}")
                    retries  += 1
                    continue

                try:
                    #  Wait for ACK
                    data, addr = sock.recvfrom(4096)
                    pkt = decode_packet(data)
                except socket.timeout as e:
                    log(f"Error receiving ACK: {e}")
                    retries += 1
                    continue

                # Validate ACK
                if pkt["flags"] & FLAG_ACK and pkt["ack"] == seq:
                    log(f"RECEIVED ACK for seq={seq}")
                    break # ACK is good, move on to next message
                elif pkt["ack"] < seq:
                    log(f"Ignoring stale ACK={pkt['ack']} (current seq={seq})")
                    continue     # do NOT count as retry, just wait again for correct ACK
                else:
                    log(f"Unexpected ACK received: {pkt}")
                    retries += 1


            if retries > args.max_retries:
                log(f"FAILED to send message after {args.max_retries} retries: seq={seq}")
            else:
                log(f"Message seq={seq} delivered")

            seq += 1
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt received. Exiting...")

    finally:
        print("\nClosing socket...")
        sock.close()
        log("Client stopped cleanly.")
        plot_client_graph("./logs/client.log")

if __name__ == "__main__":
    main()