import socket
import sys
import argparse
import random
import time

from samba.dcerpc.smbXsrv import client

from logger import make_logger


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--listen-ip", required=True) # IP address to bind for client packets
    parser.add_argument("--listen-port", type=int, required=True) # Port to listen on for client packets
    parser.add_argument("--target-ip", required=True) # Server IP address to forward packets to
    parser.add_argument("--target-port", type=int, required=True) # Server port number

    # drop and delay rules
    parser.add_argument("--client-drop", type=int, default=0)
    parser.add_argument("--server-drop", type=int, default=0)
    parser.add_argument("--client-delay", type=int, default=0)
    parser.add_argument("--server-delay", type=int, default=0)
    parser.add_argument("--client-delay-time-min", type=int, default=0)
    parser.add_argument("--client-delay-time-max", type=int, default=0)
    parser.add_argument("--server-delay-time-min", type=int, default=0)
    parser.add_argument("--server-delay-time-max", type=int, default=0)

    args = parser.parse_args()
    log = make_logger("proxy.log")


    # 1: client -> proxy 2: proxy -> server 3: proxy <- server 4: client <- proxy
    # client: sends to proxy, receives from proxy (proxy address)
    # proxy: open to incoming data (forwards data to server), receives data from server (forwards to client)
    # server: receives data from proxy, sends data to proxy

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except OSError as e:
        log(f"ERROR: Could not create socket: {e}")
        sys.exit(1)

    # Bind only to proxy’s listen address
    try:
        sock.bind((args.listen_ip, args.listen_port))
        log(f"Proxy listening on {args.listen_ip}:{args.listen_port}")
    except OSError as e:
        log(f"ERROR: Could not bind proxy: {e}")
        sys.exit(1)

    # store server tuple
    server_addr = (args.target_ip, args.target_port)

    client_addr = None   # we learn this dynamically when first client packet arrives

    # while loop for taking in and sending out data,
    try:
        while True:
            data, addr = sock.recvfrom(4096)

            # determine direction
            if client_addr is None:
                # first time we hear from client
                client_addr = addr
                log(f"Detected FIRST client: {client_addr}")

            if addr == client_addr:
                # client -> proxy -> server
                log(f"FROM CLIENT {addr} | {data!r}")

                # drop?
                if random.randint(1, 100) <= args.client_drop:
                    log("DROP (client→server)")
                    continue

                # delay?
                if args.client_delay:
                    delay = random.uniform(args.client_delay_time_min,
                                           args.client_delay_time_max)
                    log(f"DELAY {delay:.3f}s (client→server)")
                    time.sleep(delay)

                # forward to server
                sock.sendto(data, server_addr)
                log("FORWARDED to server")

            else:
                # server -> proxy -> client
                log(f"FROM SERVER {addr} | {data!r}")

                # drop?
                if random.randint(1, 100) <= args.server_drop:
                    log("DROP (server→client)")
                    continue

                # delay?
                if args.server_delay:
                    delay = random.uniform(args.server_delay_time_min,
                                           args.server_delay_time_max)
                    log(f"DELAY {delay:.3f}s (server→client)")
                    time.sleep(delay)

                # forward to client
                if client_addr:
                    sock.sendto(data, client_addr)
                    log("FORWARDED to client")

    except KeyboardInterrupt:
        print("\nProxy shutting down...")

    finally:
        sock.close()
        log("Proxy closed cleanly.")

if __name__ == "__main__":
    main()