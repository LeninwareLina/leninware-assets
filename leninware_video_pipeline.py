# leninware_video_pipeline.py

import os
from typing import List
from config import USE_MOCK_AI

from shotstack_renderer import render_video_with_shotstack


def create_leninware_video(
    script_text: str,
    image_paths: List[str],
    audio_path: str,
    workdir: str = "/tmp/leninware",
) -> str:
    """
    Pipeline:
    - real mode: send assets to Shotstack and render full video
    - mock mode: create a tiny dummy .mp4 with no external API calls
    """

    os.makedirs(workdir, exist_ok=True)
    video_path = os.path.join(workdir, "final.mp4")

    # ----------------------------------------------------
    # MOCK MODE → generate a tiny placeholder MP4
    # ----------------------------------------------------
    if USE_MOCK_AI:
        print("[pipeline] MOCK: Creating placeholder video...")

        # A minimal MP4 header for a valid zero-duration video
        dummy_mp4 = (
            b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42mp41"
        )

        with open(video_path, "wb") as f:
            f.write(dummy_mp4)

        print("[pipeline] MOCK: Video complete:", video_path)
        return video_path

    # ----------------------------------------------------
    # REAL MODE → use Shotstack
    # ----------------------------------------------------
    print("[pipeline] Rendering Shotstack video...")
    render_video_with_shotstack(
        audio_file=audio_path,
        image_files=image_paths,
        script_text=script_text,
        output_video_path=video_path,
    )

    print("[pipeline] Video complete:", video_path)
    return video_path