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
    - mock mode: generate tiny placeholder MP4
    - real mode: render via Shotstack
    """

    print("\n[pipeline] ===== Video Pipeline Starting =====")
    print(f"[pipeline] workdir: {workdir}")
    print(f"[pipeline] audio path: {audio_path}")
    print(f"[pipeline] image count: {len(image_paths)}")

    os.makedirs(workdir, exist_ok=True)
    video_path = os.path.join(workdir, "final.mp4")

    # ----------------------------------------------------
    # MOCK MODE
    # ----------------------------------------------------
    if USE_MOCK_AI:
        print("[pipeline:mock] Mock mode enabled — skipping Shotstack.")
        print(f"[pipeline:mock] Creating tiny placeholder MP4 at {video_path}")

        try:
            dummy_mp4 = b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42mp41"
            with open(video_path, "wb") as f:
                f.write(dummy_mp4)
        except Exception as e:
            print(f"[pipeline:mock] ERROR writing dummy MP4: {e}")
            raise

        print("[pipeline:mock] Mock video complete.\n")
        return video_path

    # ----------------------------------------------------
    # REAL MODE — Shotstack renderer
    # ----------------------------------------------------
    print("[pipeline] Real mode — invoking Shotstack renderer...")
    print(f"[pipeline] Rendering with {len(image_paths)} images and audio.")

    try:
        render_video_with_shotstack(
            audio_file=audio_path,
            image_files=image_paths,
            script_text=script_text,
            output_video_path=video_path,
        )
    except Exception as e:
        print(f"[pipeline] ERROR during Shotstack render: {e}")
        raise

    print(f"[pipeline] Video rendering complete → {video_path}")
    print("[pipeline] =====================================\n")

    return video_path