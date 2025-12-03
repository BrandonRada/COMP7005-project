import os

def main():
    log_dir = "./logs"
    log_files = ["client.log", "server.log", "proxy.log"]

    # make sure logs/ exists
    if not os.path.exists(log_dir):
        print("[clear_logs] logs/ directory does not exist, creating it...")
        os.makedirs(log_dir)

    for log in log_files:
        path = os.path.join(log_dir, log)
        try:
            # open with write mode truncates to 0 bytes
            with open(path, "w") as f:
                pass
            print(f"[clear_logs] Cleared {path}")
        except Exception as e:
            print(f"[clear_logs] ERROR clearing {path}: {e}")

    print("[clear_logs] Done.")


if __name__ == "__main__":
    main()
