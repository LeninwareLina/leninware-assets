LENINWARE AUTOMATED VIDEO PIPELINE
==================================

This project generates fully automated political reaction videos using:
- YouTube ingestion
- Virality filtering
- TranscriptAPI (transcriptapi.com)
- Leninware commentary generation
- Script-level safety filtering
- Storyboard prompt generation (GPT-4o-mini)
- Image generation (OpenAI Image API)
- TTS (voice: Michelle, 1.2x speed)
- Shotstack rendering (images + captions + audio)
- Automatic YouTube uploads

The goal is to produce videos that are politically sharp and critical of
capitalism, imperialism, and systemic injustice, while still staying within the
general safety and moderation boundaries of text, image, and video platforms.

-----------------------------------
FOLDER STRUCTURE
-----------------------------------

main.py
    The primary pipeline runner.

audio_generator.py
    Generates TTS audio from the filtered script.

config.py
    Loads environment variables and API keys.
    Includes URLs for TranscriptAPI, Shotstack, and OpenAI.

image_generator.py
    Generates images using OpenAI's image model.

leninware_commentary.py
    Produces the main Leninware commentary from a transcript source.

leninware_video_pipeline.py
    Connects TTS, images, captions, and Shotstack to produce a video.

safe_image_prompt_filter.py
    Rule-based filter that applies substitutions to storyboard prompts to keep
    the output compliant with YouTube policy. Does not remove political content.

shotstack_renderer.py
    Sends image, caption, and audio instructions to Shotstack and retrieves the
    final MP4.

storyboard_prompt_generator.py
    Uses GPT-4o-mini to convert the commentary script into symbolic image prompts.
    Avoids real persons, copyrighted characters, graphic violence, or other
    content that would break OpenAI’s image rules.

transcript_fetcher.py
    Pulls transcripts using TranscriptAPI v2.

youtube_ingest.py
    Reads channel IDs from prompts/youtube_channels.txt and fetches recent videos.

youtube_virality_worker.py
    Selects the most “viral” or promising recent videos for commentary.

youtube_uploader.py
    Uploads the final rendered video to YouTube.


-----------------------------------
PROMPTS FOLDER
-----------------------------------

prompts/leninware_raw.txt
    The base prompt used to generate Leninware’s political commentary voice.

prompts/safe_substitution_rules.txt
    Simple substitution rules applied to storyboard prompts to avoid OpenAI or
    YouTube moderation issues.

prompts/script_safety_filter.txt
    Defines which content is allowed and what must be rewritten for compliance.

prompts/youtube_channels.txt
    One YouTube channel ID per line. The ingest system pulls only from channels
    listed here.


-----------------------------------
PIPELINE OVERVIEW
-----------------------------------

1. youtube_ingest → Fetch recent videos from configured channels
2. youtube_virality_worker → Choose the best candidate
3. transcript_fetcher → Request transcript from TranscriptAPI
4. leninware_commentary → Generate political commentary
5. script_safety_filter → Remove only content unsafe for platform rules
6. storyboard_prompt_generator → Build symbolic scene prompts
7. safe_image_prompt_filter → Apply rule-based substitutions
8. image_generator → Generate images from prompts
9. audio_generator → Convert script into TTS audio (Michelle, 1.2x)
10. shotstack_renderer → Assemble audio, images, and captions into a video
11. youtube_uploader → Upload the final MP4 to YouTube


-----------------------------------
REQUIRED ENVIRONMENT VARIABLES
-----------------------------------

OPENAI_API_KEY
YOUTUBE_API_KEY
SHOTSTACK_API_KEY
TRANSCRIPT_API_KEY

YOUTUBE_CLIENT_ID
YOUTUBE_CLIENT_SECRET
YOUTUBE_REFRESH_TOKEN

-----------------------------------
NOTES
-----------------------------------

- Political analysis remains fully radical and system-critical.
- Safety filtering is minimal and designed only to avoid:
    * platform takedowns
    * OpenAI moderation blocks
    * graphic or targeted prohibited content
- The image pipeline is symbolic by design and avoids real individuals.
- audio_generator.py is mobile-friendly — no ffmpeg or pydub required.
- The entire system can run on a mobile device with a decent Python environment.

-----------------------------------
LICENSE
-----------------------------------

This project is provided as-is. No warranty is offered. Use responsibly and
within platform terms of service.
