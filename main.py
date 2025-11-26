# main.py

from youtube_virality_worker import run_virality_pass


def main():
    print("[main] Starting Leninware pipeline single pass...")
    run_virality_pass()
    print("[main] Leninware pass complete.")


if __name__ == "__main__":
    main()