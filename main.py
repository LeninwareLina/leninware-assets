# main.py
"""
Entry-point for Railway.
Runs the virality worker once at startup.
"""

from youtube_virality_worker import run_virality_pass

if __name__ == "__main__":
    run_virality_pass()