# plot_logs.py
import matplotlib.pyplot as plt
import re
from datetime import datetime
import os

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def parse_time(line):
    m = re.match(r"\[(.*?)\]", line)
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
    except:
        return None


# -------------------------------------------------
# CLIENT LOGS
# -------------------------------------------------
def parse_client(file):
    sent = 0
    acked = 0
    retrans = 0

    with open(file, "r") as f:
        for line in f:
            if "SENT |" in line:
                sent += 1
                m = re.search(r"retries=(\d+)", line)
                if m and int(m.group(1)) > 0:
                    retrans += 1

            if "RECEIVED ACK" in line:
                acked += 1

    return sent, acked, retrans


def plot_client_graph(file):
    if not os.path.exists(file):
        print(f"[plot] No client log exists: {file}")
        return

    sent, acked, retrans = parse_client(file)

    plt.figure(figsize=(7, 5))
    plt.bar(["Sent", "Acked", "Retransmissions"], [sent, acked, retrans])
    plt.title("Client Summary Statistics")
    plt.tight_layout()
    plt.savefig("client_graph.png")
    print("[plot] Saved client_graph.png")


# -------------------------------------------------
# SERVER LOGS
# -------------------------------------------------
def parse_server(file):
    received = 0
    with open(file, "r") as f:
        for line in f:
            if "RECEIVED" in line:
                received += 1
    return received


def plot_server_graph(file):
    if not os.path.exists(file):
        print(f"[plot] No server log exists: {file}")
        return

    received = parse_server(file)

    plt.figure(figsize=(7, 5))
    plt.bar(["Received"], [received])
    plt.title("Server Summary Statistics")
    plt.tight_layout()
    plt.savefig("server_graph.png")
    print("[plot] Saved server_graph.png")


# -------------------------------------------------
# PROXY LOGS
# -------------------------------------------------
import os
import matplotlib.pyplot as plt

def parse_proxy(file):
    stats = {
        "drops_total": 0,
        "drops_client": 0,
        "drops_server": 0,

        "delays_total": 0,
        "delays_client": 0,
        "delays_server": 0,

        "fwd_total": 0,
        "fwd_to_server": 0,
        "fwd_to_client": 0
    }

    with open(file, "r") as f:
        for line in f:
            # ---------------- DROP ----------------
            if "DROP" in line:
                stats["drops_total"] += 1
                if "(client -> server)" in line:
                    stats["drops_client"] += 1
                elif "(server -> client)" in line:
                    stats["drops_server"] += 1

            # ---------------- DELAY ----------------
            if "DELAY" in line:
                stats["delays_total"] += 1
                if "(client -> server)" in line:
                    stats["delays_client"] += 1
                elif "(server -> client)" in line:
                    stats["delays_server"] += 1

            # ---------------- FORWARDED ----------------
            if "FORWARDED" in line:
                stats["fwd_total"] += 1
                if "to server" in line:
                    stats["fwd_to_server"] += 1
                elif "to client" in line:
                    stats["fwd_to_client"] += 1

    return stats


def plot_proxy_graph(file):
    if not os.path.exists(file):
        print(f"[plot] No proxy log exists: {file}")
        return

    s = parse_proxy(file)

    labels = [
        "Dropped (total)", "Dropped (client)", "Dropped (server)",
        "Delayed (total)", "Delayed (client)", "Delayed (server)",
        "Forwarded (total)", "Forwarded -> Server", "Forwarded -> Client"
    ]

    values = [
        s["drops_total"], s["drops_client"], s["drops_server"],
        s["delays_total"], s["delays_client"], s["delays_server"],
        s["fwd_total"], s["fwd_to_server"], s["fwd_to_client"]
    ]

    plt.figure(figsize=(10, 6))
    plt.bar(labels, values)
    plt.title("Proxy Summary Statistics")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig("proxy_graph.png")
    print("[plot] Saved proxy_graph.png")
