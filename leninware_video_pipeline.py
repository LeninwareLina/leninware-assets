#leninware_video_pipeline.py

import os
from typing import List

from audio_generator import generate_tts_audio
from shotstack_renderer import render_video_with_shotstack


def create_leninware_video(
    safe_script_text: str,
    image_paths: List[str],
    workdir: str = "/tmp/leninware",
) -> str:
    """
    Pipeline:
    - safe script -> TTS (Michelle, 1.2x)
    - audio + images + captions -> Shotstack video
    """
    os.makedirs(workdir, exist_ok=True)

    audio_path = os.path.join(workdir, "tts.wav")
    video_path = os.path.join(workdir, "final.mp4")

    print("[pipeline] Generating TTS audio...")
    generate_tts_audio(safe_script_text, audio_path)

    print("[pipeline] Rendering Shotstack video...")
    render_video_with_shotstack(
        audio_file=audio_path,
        image_files=image_paths,
        script_text=safe_script_text,
        output_video_path=video_path,
    )

    print("[pipeline] Video complete:", video_path)
    return video_path