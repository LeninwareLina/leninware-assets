# main.py

from youtube_virality_worker import run_virality_pass


def main():
    """
    Entry point for Leninware pipeline.

    Right now this:
    - fetches candidate videos
    - scores them
    - picks winners
    - runs: transcript -> Leninware commentary -> image prompts -> images
    - calls Shotstack stub

    You can schedule this with Railway's cron or call manually.
    """
    run_virality_pass()


if __name__ == "__main__":
    main()