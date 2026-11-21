import re
import json
import urllib.request
import urllib.parse
from datetime import datetime
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi

def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from various YouTube URL formats."""
    if not url:
        return ""
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})',
        r'([a-zA-Z0-9_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url.strip())
        if match:
            return match.group(1)
    return ""

def get_video_metadata(url: str) -> dict:
    """Fetch video metadata using yt-dlp with oEmbed fallback."""
    video_id = extract_video_id(url)
    clean_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else url
    
    meta = {
        "video_id": video_id,
        "youtube_url": clean_url,
        "title": "Untitled Video",
        "channel_name": "Tech Channel",
        "description": "",
        "thumbnail": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg" if video_id else "",
        "duration": 0,
        "duration_str": "5 min read",
        "tags": ["Tech", "Tutorial"]
    }
    
    # Try yt-dlp first
    try:
        ydl_opts = {
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=False)
            if info:
                meta["title"] = info.get('title') or meta["title"]
                meta["channel_name"] = info.get('uploader') or info.get('channel') or meta["channel_name"]
                meta["description"] = info.get('description', '')[:1000]
                meta["thumbnail"] = info.get('thumbnail') or meta["thumbnail"]
                duration = info.get('duration', 0)
                meta["duration"] = duration
                if duration:
                    mins = max(1, round(duration / 60))
                    meta["duration_str"] = f"{mins} min read"
                if info.get('tags'):
                    meta["tags"] = info['tags'][:5]
                return meta
    except Exception as e:
        print(f"yt-dlp error (falling back): {e}")

    # Fallback to YouTube oEmbed API
    try:
        oembed_url = f"https://www.youtube.com/oembed?url={urllib.parse.quote(clean_url)}&format=json"
        req = urllib.request.Request(oembed_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            meta["title"] = data.get("title", meta["title"])
            meta["channel_name"] = data.get("author_name", meta["channel_name"])
            meta["thumbnail"] = data.get("thumbnail_url", meta["thumbnail"])
    except Exception as e:
        print(f"oEmbed fallback error: {e}")

    return meta

def get_transcript(video_id: str) -> str:
    """Fetch video transcript if available."""
    if not video_id:
        return ""
    try:
        if hasattr(YouTubeTranscriptApi, 'get_transcript'):
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'hi', 'en-IN'])
            return " ".join([item['text'] for item in transcript_list])
        elif hasattr(YouTubeTranscriptApi, 'fetch'):
            ytt = YouTubeTranscriptApi()
            snippets = ytt.fetch(video_id, languages=['hi', 'en'])
            return " ".join([s.text for s in snippets])
    except Exception as e:
        print(f"Transcript fetch note: {e}")
    return ""

def slugify(text: str) -> str:
    """Create a URL-safe slug from title."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text).strip('-')
    return text[:60] or "tech-post"
