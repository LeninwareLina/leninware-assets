# run_pipeline.py

from yt_reaction_pipeline.youtube_ingest import get_recent_candidates
from yt_reaction_pipeline.youtube_virality_worker import run_virality_pass
from yt_reaction_pipeline.transcript_fetcher import fetch_transcript

from yt_reaction_pipeline.summary_engine import summarize_transcript
from yt_reaction_pipeline.commentary_engine import generate_commentary
from yt_reaction_pipeline.script_safety_filter import apply_script_safety_filter

from yt_reaction_pipeline.storyboard_engine import generate_storyboard_prompts
from yt_reaction_pipeline.prompt_filter import apply_safe_substitutions
from yt_reaction_pipeline.image_engine import generate_images_from_prompts

from yt_reaction_pipeline.audio_engine import generate_tts_audio
from yt_reaction_pipeline.video_renderer import render_reaction_video

from yt_reaction_pipeline.youtube_uploader import upload_video
from config import USE_MOCK_AI, ENABLE_YOUTUBE_UPLOAD


def main():
    print("\n===== YouTube Reaction Pipeline Starting =====\n")

    # 1. INGEST VIDEO CANDIDATES
    print("[pipeline] (1) Fetching recent candidates...")
    candidates = get_recent_candidates(max_results=5)
    if not candidates:
        print("[pipeline] No recent long-form videos found.")
        return

    # 2. VIRALITY RANKING
    print("[pipeline] (2) Running virality pass...")
    viral_list = run_virality_pass(candidates)
    if not viral_list:
        print("[pipeline] No videos with usable stats.")
        return

    print("\n[pipeline] Virality ranking:")
    for v in viral_list:
        print(f"  {v['title']} — score={v['virality']}")

    # 3. TRANSCRIPT SELECTION
    selected = None
    transcript_text = None

    for v in viral_list:
        print(f"\n[pipeline] (3) Checking transcript availability for: {v['title']}")
        tr = fetch_transcript(v["video_id"])
        if tr:
            transcript_text = tr
            selected = v
            break

    if not selected:
        print("[pipeline] No videos with available transcripts.")
        return

    print(f"\n[pipeline] Selected video:\n    Title: {selected['title']}\n    URL: {selected['url']}\n")

    # 4. TRANSCRIPT SUMMARY
    print("[pipeline] (4) Summarizing transcript...")
    summary_text = summarize_transcript(
        transcript_text,
        channel_name=selected.get("channel_title", ""),
        author_name=selected.get("channel_title", ""),  # YouTube channel owner = author
        video_title=selected["title"]
    )

    # 5. GENERATE COMMENTARY
    print("[pipeline] (5) Generating commentary from summary...")
    raw_commentary = generate_commentary(
        summary=summary_text,
        channel_name=selected.get("channel_title", ""),
        author_name=selected.get("channel_title", ""),
        video_title=selected["title"]
    )

    # 6. SAFETY FILTER
    print("[pipeline] (6) Applying script safety filter...")
    safe_script = apply_script_safety_filter(raw_commentary)

    # 7. STORYBOARD
    print("[pipeline] (7) Generating storyboard prompts...")
    storyboard = generate_storyboard_prompts(safe_script)

    # 8. IMAGE PROMPT FILTERING
    print("[pipeline] (8) Applying substitution safety filter...")
    safe_prompts = apply_safe_substitutions(storyboard)

    # 9. IMAGE GENERATION
    print("[pipeline] (9) Generating images from prompts...")
    image_paths = generate_images_from_prompts(safe_prompts)

    # 10. TTS AUDIO
    print("[pipeline] (10) Generating TTS audio...")
    audio_path = generate_tts_audio(
        text=safe_script,
        output_path="output/audio.wav"
    )

    # 11. VIDEO RENDERING
    print("[pipeline] (11) Rendering final reaction video...")
    video_path = render_reaction_video(
        script_text=safe_script,
        image_paths=image_paths,
        audio_path=audio_path
    )

    print(f"[pipeline] Render complete: {video_path}")

    # 12. UPLOAD
    if USE_MOCK_AI:
        print("[pipeline] (12) MOCK MODE — upload disabled automatically.")
    elif not ENABLE_YOUTUBE_UPLOAD:
        print("[pipeline] (12) Upload disabled — skipping YouTube upload.")
    else:
        print("[pipeline] (12) Uploading to YouTube...")
        upload_video(
            video_path,
            title=f"Reaction: {selected['title']}",
            description=(
                f"Automated reaction to: {selected['title']}\n"
                f"Original video: {selected['url']}\n"
            )
        )

    print("\n===== YouTube Reaction Pipeline Complete =====\n")


if __name__ == "__main__":
    main()