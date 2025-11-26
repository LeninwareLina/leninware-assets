import os
from audio_generator import generate_tts_audio
from shotstack_renderer import render_video_with_shotstack


def create_leninware_video(transcript_text: str, workdir: str = "/tmp/leninware") -> str:
    """
    Main pipeline: TTS → MP4 render → return final path.
    """

    os.makedirs(workdir, exist_ok=True)

    audio_path = os.path.join(workdir, "tts.wav")
    video_path = os.path.join(workdir, "final.mp4")

    print("[pipeline] Generating TTS audio...")
    generate_tts_audio(transcript_text, audio_path)

    print("[pipeline] Rendering Shotstack video...")
    render_video_with_shotstack(audio_path, video_path)

    print("[pipeline] Video complete:", video_path)
    return video_path