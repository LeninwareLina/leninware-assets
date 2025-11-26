# leninware_video_pipeline.py

from youtube_virality_worker import run_virality_pass


def run_single_pass():
    """
    Convenience entrypoint to run a single virality pass.
    """
    run_virality_pass()