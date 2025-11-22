# youtube_virality_worker.py
#
# Periodically:
#  - pulls candidate videos from youtube_ingest
#  - scores them with an ideology-aware virality engine
#  - sends the best ones into the Leninware video pipeline

import math
from datetime import datetime, timezone

import youtube_ingest  # uses your existing ingest module
from leninware_video_pipeline import generate_leninware_tts_from_url

# -----------------------------
# Config
# -----------------------------

# How many top videos to actually send to Leninware on each run
MAX_VIDEOS_PER_RUN = 3

# Minimum score required to be considered “viral enough”
VIRALITY_THRESHOLD = 2.2


# -----------------------------
# Helpers
# -----------------------------

def _parse_iso_datetime(dt_str: str | None) -> datetime | None:
    if not dt_str:
        return None
    try:
        # Handles ISO like "2025-11-22T14:03:15Z"
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except Exception:
        return None


def _safe_num(value, default=0):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


# -----------------------------
# Virality / Ideology Scoring
# -----------------------------

def compute_leninware_virality_score(video: dict) -> float:
    """
    Ideology-aware virality score.

    Expects a dict with (when available):
      title, description, url, channel_title, tags,
      view_count, like_count, comment_count, published_at
    Any missing fields are safely treated as 0 / "".
    """
    title = (video.get("title") or "").strip()
    description = (video.get("description") or "").strip()
    channel = (video.get("channel_title") or "").strip()
    tags = video.get("tags") or []

    full_text = " ".join([title, description, " ".join(tags)]).lower()
    channel_lower = channel.lower()

    views = _safe_num(video.get("view_count"))
    likes = _safe_num(video.get("like_count"))
    comments = _safe_num(video.get("comment_count"))

    # --- Popularity / velocity ---

    published_at = _parse_iso_datetime(video.get("published_at"))
    if published_at is None:
        age_hours = 48.0  # assume older if we can't parse
    else:
        delta = datetime.now(timezone.utc) - published_at
        age_hours = max(delta.total_seconds() / 3600.0, 1.0)

    # View velocity: views per hour, squashed + log scaled
    views_per_hour = views / age_hours
    # Roughly:
    #  0  -> 0
    #  100/h  -> ~1.3
    #  1k/h   -> ~2.0
    #  10k/h  -> ~2.6–3.0
    popularity_score = math.log10(views_per_hour + 10) - 1
    popularity_score = max(0.0, min(popularity_score, 3.0))

    # Engagement: likes + comments relative to views
    if views <= 0:
        engagement_rate = 0.0
    else:
        engagement_rate = ((likes * 2.0) + (comments * 3.0)) / views
        # Clamp to sane [0, 0.1] range then scale
        engagement_rate = max(0.0, min(engagement_rate, 0.1))
    engagement_score = engagement_rate * 20.0  # 0–2.0 approx

    # --- Ideology / content type bonuses ---

    ideology_bonus = 0.0

    # Explicit fascism / empire / genocide / class conflict
    ideology_keywords_strong = [
        "fascist", "fascism", "nazis", "neo-nazi", "white nationalist",
        "genocide", "ethnic cleansing",
        "gaza", "palestine", "i state", "israel", "west bank",
        "coup", "junta", "authoritarian",
        "strike", "union", "labor union", "workers", "scab",
        "billionaire", "oligarch",
        "police shooting", "police violence", "riot police",
    ]
    if any(k in full_text for k in ideology_keywords_strong):
        ideology_bonus += 1.0

    # Mainstream bourgeois politics / imperial management
    ideology_keywords_medium = [
        "trump", "donald", "biden", "kamala", "netanyahu",
        "supreme court", "congress", "senate", "parliament",
        "republicans", "democrats", "tories", "labour", "labour party",
        "election", "vote", "campaign",
        "ukraine", "nato", "russia", "china", "iran",
        "sanctions", "military aid",
    ]
    if any(k in full_text for k in ideology_keywords_medium):
        ideology_bonus += 0.8

    # Corruption / scandal / leaks / big money
    ideology_keywords_soft = [
        "corruption", "bribery", "dark money", "lobbyist",
        "offshore", "tax haven", "money laundering",
        "oil company", "defense contractor",
        "arms deal", "spyware", "surveillance",
    ]
    if any(k in full_text for k in ideology_keywords_soft):
        ideology_bonus += 0.5

    # --- Channel category bonuses ---

    # Liberal / centrist news we want to drag
    liberal_news_channels = [
        "cnn", "msnbc", "nbc news", "abc news", "cbs news",
        "bbc", "bbc news", "sky news",
        "meidas", "meidastouch",
    ]
    if any(name in channel_lower for name in liberal_news_channels):
        ideology_bonus += 0.7

    # Progressive commentary / podcast circles
    lefty_channels = [
        "secular talk", "kyle kulinski", "the majority report",
        "majority report", "tyt", "the young turks",
        "hassanabi", "hassan abbi", "chapotraphouse", "chapo",
    ]
    if any(name in channel_lower for name in lefty_channels):
        ideology_bonus += 0.9

    # --- Drama / “this will trend” language ---

    drama_keywords = [
        "exposed", "debunked", "meltdown", "rage", "loses it",
        "destroyed", "roasted", "obliterated", "called out",
        "goes off", "claps back", "freakout", "rants",
        "bombshell", "shocking", "secret recording",
    ]
    if any(k in full_text for k in drama_keywords):
        ideology_bonus += 0.6

    # --- Final weighted score ---

    score = 0.0
    score += popularity_score * 0.8      # up to ~2.4
    score += engagement_score * 0.6      # up to ~1.2
    score += ideology_bonus              # 0–~3 depending on content

    return round(score, 2)


# -----------------------------
# Candidate retrieval
# -----------------------------

def get_candidate_videos() -> list[dict]:
    """
    Thin wrapper so we don't care which function name youtube_ingest uses.
    It just has to return a list[dict] of videos.
    """
    # Try common function names in order
    if hasattr(youtube_ingest, "get_candidate_videos"):
        return youtube_ingest.get_candidate_videos()
    if hasattr(youtube_ingest, "fetch_recent_videos"):
        return youtube_ingest.fetch_recent_videos()
    if hasattr(youtube_ingest, "get_recent_videos"):
        return youtube_ingest.get_recent_videos()

    raise RuntimeError(
        "youtube_ingest module is missing a video-fetch function. "
        "Expected one of: get_candidate_videos, fetch_recent_videos, get_recent_videos."
    )


# -----------------------------
# Main worker
# -----------------------------

def main():
    print("=== Leninware YouTube Virality Worker ===")

    try:
        videos = get_candidate_videos()
    except Exception as e:
        print(f"Error fetching videos from youtube_ingest: {e}")
        return

    if not videos:
        print("No candidate videos returned.")
        return

    scored = []
    for video in videos:
        score = compute_leninware_virality_score(video)

        title = (video.get("title") or "").strip()
        url = video.get("url") or video.get("video_url") or "UNKNOWN_URL"

        print(f"\nTitle: {title}")
        print(f"URL:   {url}")
        print(f"Score: {score}")

        scored.append((score, video))

    # Sort best first
    scored.sort(key=lambda x: x[0], reverse=True)

    # Filter by threshold
    eligible = [v for (s, v) in scored if s >= VIRALITY_THRESHOLD]

    if not eligible:
        print("\nNo videos crossed virality threshold "
              f"({VIRALITY_THRESHOLD}). Nothing sent to Leninware this run.")
        return

    print(f"\n{len(eligible)} videos passed threshold {VIRALITY_THRESHOLD}.")
    to_process = eligible[:MAX_VIDEOS_PER_RUN]

    for idx, video in enumerate(to_process, start=1):
        title = (video.get("title") or "").strip()
        url = video.get("url") or video.get("video_url")
        if not url:
            print(f"[{idx}] Skipping video with no URL: {title}")
            continue

        print(f"\n[{idx}] Generating Leninware TTS for:")
        print(f"Title: {title}")
        print(f"URL:   {url}")

        try:
            tts_text = generate_leninware_tts_from_url(url)
            print("\n--- Leninware TTS ---")
            print(tts_text)
            print("---------------------\n")
        except Exception as e:
            print(f"Error running Leninware pipeline for {url}: {e}")


if __name__ == "__main__":
    main()