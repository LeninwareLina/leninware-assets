# main.py — Leninware scheduler controller

import time
import datetime
import traceback

from youtube_virality_worker import run_virality_pass


# ───────────────────────────────────────────────────────────────
# Scheduler Config
# ───────────────────────────────────────────────────────────────

INTERVAL_MINUTES = 20      # run every 20 minutes
START_HOUR = 10            # earliest activity (10:00)
END_HOUR = 23              # latest activity (23:00)


def should_run_now(now: datetime.datetime) -> bool:
    """
    Only run between 10:00 and 23:00 (inclusive).
    """
    return START_HOUR <= now.hour <= END_HOUR


# ───────────────────────────────────────────────────────────────
# Main Loop
# ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Leninware Scheduler Online ===")
    print(f"Active hours: {START_HOUR}:00 → {END_HOUR}:00")
    print(f"Interval: {INTERVAL_MINUTES} minutes")
    print("--------------------------------------------------\n")

    while True:
        now = datetime.datetime.now()

        if should_run_now(now):
            print(f"[{now}] Triggering virality scan...")
            try:
                run_virality_pass()
            except Exception as e:
                print("\nERROR during virality pass:")
                print(str(e))
                traceback.print_exc()
                print("\nContinuing scheduler loop...\n")
        else:
            print(f"[{now}] Outside active window — idle.")

        print(f"Sleeping {INTERVAL_MINUTES} minutes...\n")
        time.sleep(INTERVAL_MINUTES * 60)