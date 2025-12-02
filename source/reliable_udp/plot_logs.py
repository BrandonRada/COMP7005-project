import matplotlib.pyplot as plt
import re
from datetime import datetime

# --------------------------------------------
# Time parser for log timestamps
# --------------------------------------------
def parse_time(line):
    m = re.match(r"\[(.*?)\]", line)
    if not m:
        return None
    ts = m.group(1)
    try:
        return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
    except:
        return None

# --------------------------------------------
# Parse client log (sent, ack, retries)
# --------------------------------------------
def parse_client_log(file):
    events = []
    with open(file, "r") as f:
        for line in f:
            t = parse_time(line)
            # SENT | seq=3 retries=2
            m = re.search(r"SENT \| seq=(\d+) retries=(\d+)", line)
            if m:
                seq = int(m.group(1))
                retries = int(m.group(2))
                events.append(("sent", seq, retries, t))

            # RECEIVED ACK for seq=3
            m = re.search(r"ACK.*seq=(\d+)", line)
            if m:
                seq = int(m.group(1))
                events.append(("ack", seq, None, t))
    return events

# --------------------------------------------
# Parse proxy log (drops, delays, forwards)
# --------------------------------------------
def parse_proxy_log(file):
    events = []
    with open(file, "r") as f:
        for line in f:
            t = parse_time(line)

            # DROP
            if "DROP" in line:
                m = re.search(r"seq=(\d+)", line)
                seq = int(m.group(1)) if m else None
                events.append(("drop", seq, t))

            # FORWARDED
            elif "FORWARDED to server" in line or "FORWARDED to client" in line:
                m = re.search(r"seq=(\d+)", line)
                seq = int(m.group(1)) if m else None
                events.append(("forward", seq, t))

            # DELAY
            if "DELAY" in line:
                m = re.search(r"seq=(\d+)", line)
                seq = int(m.group(1)) if m else None
                events.append(("delay", seq, t))

    return events

# --------------------------------------------
# Parse server log (received)
# --------------------------------------------
def parse_server_log(file):
    events = []
    with open(file, "r") as f:
        for line in f:
            t = parse_time(line)
            m = re.search(r"seq=(\d+)", line)
            if m:
                seq = int(m.group(1))
                events.append(("recv", seq, t))
    return events

# --------------------------------------------
# Load everything
# --------------------------------------------
client_events = parse_client_log("./logs/client.log")
proxy_events = parse_proxy_log("./logs/proxy.log")
server_events = parse_server_log("./logs/server.log")

# --------------------------------------------
# Build summary numbers
# --------------------------------------------
sent_count = len([e for e in client_events if e[0] == "sent"])
ack_count = len([e for e in client_events if e[0] == "ack"])
drops = len([e for e in proxy_events if e[0] == "drop"])
delays = len([e for e in proxy_events if e[0] == "delay"])

# Retransmissions = number of nonzero retries
retransmissions = sum(1 for e in client_events if e[0]=="sent" and e[2] > 0)

# --------------------------------------------
# GRAPH 1 — Summary Bar Chart
# --------------------------------------------
plt.figure(figsize=(8, 5))
labels = ["Sent", "Acked", "Dropped", "Delayed", "Retransmissions"]
vals = [sent_count, ack_count, drops, delays, retransmissions]
plt.bar(labels, vals)
plt.title("Reliable UDP Summary Statistics")
plt.xlabel("Event Type")
plt.ylabel("Count")
plt.tight_layout()
plt.show()

# --------------------------------------------
# GRAPH 2 — Timeline view of packet journey
# --------------------------------------------
plt.figure(figsize=(12, 6))

# SENT packets
sent_events = [(seq, t) for (kind, seq, retries, t) in client_events if kind == "sent"]
for seq, t in sent_events:
    plt.scatter(t, seq, color="blue", s=60)

# ACK events
ack_events = [(seq, t) for (kind, seq, retries, t) in client_events if kind == "ack"]
for seq, t in ack_events:
    plt.scatter(t, seq, color="green", marker='D', s=70)

# DROPS (proxy)
drop_events = [(seq, t) for (kind, seq, t) in proxy_events if kind == "drop"]
for seq, t in drop_events:
    plt.scatter(t, seq, color="red", marker='x', s=80)

# DELAYS (proxy)
delay_events = [(seq, t) for (kind, seq, t) in proxy_events if kind == "delay"]
for seq, t in delay_events:
    plt.scatter(t, seq, color="orange", marker='s', s=70)

# Add legend elements (clean, no duplicates)
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=8, label='Sent'),
    Line2D([0], [0], marker='D', color='w', markerfacecolor='green', markersize=8, label='ACK'),
    Line2D([0], [0], marker='x', color='red', markersize=8, label='Drop'),
    Line2D([0], [0], marker='s', color='orange', markersize=8, label='Delay'),
]

plt.legend(handles=legend_elements)

plt.title("Packet Timeline Visualization")
plt.xlabel("Time")
plt.ylabel("Sequence Number")
plt.tight_layout()
plt.show()
