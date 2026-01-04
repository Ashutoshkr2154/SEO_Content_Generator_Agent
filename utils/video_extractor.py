import re
import requests
from urllib.parse import parse_qs, urlparse
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter


# =========================================
#  Extract YouTube Video ID
# =========================================
def extract_video_id(url):
    if not url:
        return None
    
    url = url.strip()

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    patterns = [
        r"(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/|youtube\.com\/e\/|youtube\.com\/watch\?.*v=|youtube\.com\/watch\?.*&v=)([^&?#]+)",
        r"youtube\.com\/shorts\/([^&?#]+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    parsed = urlparse(url)

    if "youtube.com" in parsed.netloc:
        if "watch" in parsed.path:
            q = parse_qs(parsed.query)
            if "v" in q:
                return q["v"][0]

        if "/shorts/" in parsed.path:
            parts = parsed.path.split("/")
            if "shorts" in parts:
                idx = parts.index("shorts")
                if idx + 1 < len(parts):
                    return parts[idx + 1]

    return None


# =========================================
#  Identify Platform
# =========================================
def get_video_platform(url):
    if not url:
        return "Unknown"
    
    url = url.lower()
    
    if "youtube.com" in url or "youtu.be" in url:
        return "YouTube"
    elif "instagram.com" in url:
        return "Instagram"
    elif "linkedin.com" in url:
        return "LinkedIn"
    elif "facebook.com" in url:
        return "Facebook"
    elif "tiktok.com" in url:
        return "TikTok"
    
    return "Unknown"


# =========================================
#  Transcript Fetcher (Works on ALL versions)
# =========================================
def get_transcript_text(video_id):
    """
    Supports BOTH:
    - Old API (list_transcripts)
    - New API (get_transcript)
    Always returns safe string.
    """
    try:
        # If NEW method exists
        if hasattr(YouTubeTranscriptApi, "get_transcript"):
            try:
                transcript = YouTubeTranscriptApi.get_transcript(
                    video_id,
                    languages=["en", "en-US", "en-IN"]
                )
            except:
                transcript = []

            formatter = TextFormatter()
            return formatter.format_transcript(transcript)

        # Otherwise → OLD method handling
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        try:
            transcript = transcript_list.find_transcript(["en"])
        except:
            transcript = transcript_list.find_generated_transcript(["en"])

        data = transcript.fetch()
        formatter = TextFormatter()
        return formatter.format_transcript(data)

    except Exception as e:
        print(f"⚠️ Could not fetch transcript: {e}")
        return ""


# =========================================
#  Get Metadata
# =========================================
def get_youtube_metadata(video_id):
    metadata = {
        "title": f"YouTube Video ({video_id})",
        "description": "",
        "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
        "duration": 0,
        "views": 0,
        "author": "YouTube Creator",
        "platform": "YouTube",
        "video_id": video_id,
        "transcript_text": ""
    }

    # Transcript
    metadata["transcript_text"] = get_transcript_text(video_id)

    # Scrape metadata safely
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en"
        }

        res = requests.get(url, headers=headers, timeout=10)

        if res.status_code == 200:
            html = res.text

            t = re.search(r'<meta property="og:title" content="([^"]+)"', html)
            if t: metadata["title"] = t.group(1)

            d = re.search(r'<meta property="og:description" content="([^"]+)"', html)
            if d: metadata["description"] = d.group(1)

            a = re.search(r'<link itemprop="name" content="([^"]+)"', html)
            if a: metadata["author"] = a.group(1)

            dur = re.search(r'"lengthSeconds":"(\d+)"', html)
            if dur: metadata["duration"] = int(dur.group(1))

            views = re.search(r'"viewCount":"(\d+)"', html)
            if views: metadata["views"] = int(views.group(1))

    except Exception as e:
        print(f"Metadata scraping error: {e}")

    return metadata


# =========================================
#  Main Public Function
# =========================================
def get_video_metadata(url):
    if not url:
        raise ValueError("Please enter a video URL")

    platform = get_video_platform(url)

    if platform == "YouTube":
        video_id = extract_video_id(url)
        if not video_id:
            raise ValueError("Invalid YouTube URL")
        return get_youtube_metadata(video_id)

    # Fallback for other platforms
    return {
        "title": f"Video on {platform}",
        "description": "",
        "thumbnail_url": f"https://via.placeholder.com/1280x720.png?text={platform}",
        "duration": 0,
        "views": 0,
        "author": "Unknown",
        "platform": platform,
        "video_id": "unknown",
        "transcript_text": ""
    }
