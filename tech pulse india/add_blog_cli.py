"""
Tech Pulse India CLI: Add YouTube Video as Bilingual Blog Post
Usage:
    python add_blog_cli.py --url "https://www.youtube.com/watch?v=..."
"""

import sys
import os
import argparse
import json
import uuid
from datetime import datetime
from youtube_helper import extract_video_id, get_video_metadata, get_transcript, slugify

POSTS_FILE = os.path.join(os.path.dirname(__file__), 'data', 'posts.json')

def load_posts():
    if not os.path.exists(POSTS_FILE):
        return []
    with open(POSTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_posts(posts):
    os.makedirs(os.path.dirname(POSTS_FILE), exist_ok=True)
    with open(POSTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

def add_blog_post(url, title_en=None, title_hi=None, summary_en=None, summary_hi=None,
                  takeaways_en=None, takeaways_hi=None, content_en=None, content_hi=None,
                  category="Smartphones", category_hi="स्मार्टफोन", tags=None):
    
    video_id = extract_video_id(url)
    if not video_id:
        print(f"Error: Invalid YouTube URL '{url}'")
        return None
        
    print(f"[*] Extracting metadata for Video ID: {video_id}...")
    meta = get_video_metadata(url)
    transcript = get_transcript(video_id)
    
    title_en = title_en or meta.get('title') or "Tech Breakthrough Explained"
    title_hi = title_hi or f"{title_en} (हिन्दी विश्लेषण)"
    
    channel = meta.get('channel_name', 'Tech Creator')
    
    if not summary_en:
        desc = meta.get('description', '')
        summary_en = desc[:280].replace('\n', ' ') if desc else f"In-depth tech breakdown from {channel} covering core architecture and real-world implementation."
    if not summary_hi:
        summary_hi = f"{channel} द्वारा प्रस्तुत इस वीडियो में आधुनिक तकनीक के महत्वपूर्ण पहलुओं और उपयोगिता का संपूर्ण विश्लेषण किया गया है।"
        
    if not takeaways_en:
        takeaways_en = [
            "Clear technical architectural overview and core concepts.",
            "Practical development and deployment takeaways.",
            "Future outlook and efficiency benchmarks."
        ]
    if not takeaways_hi:
        takeaways_hi = [
            "तकनीकी आर्किटेक्चर और मूलभूत सिद्धांतों की स्पष्ट समझ।",
            "डेवलपर्स के लिए व्यावहारिक कोडिंग और इंप्लीमेंटेशन टिप्स।",
            "भविष्य की उपयोगिता और परफॉरमेंस बेंचमार्क।"
        ]
        
    if not content_en:
        content_en = f"<p class=\"lead text-lg text-slate-300 mb-6\">In this featured analysis, <strong>{channel}</strong> unpacks the latest technical developments.</p><h3 class=\"text-xl font-bold text-white mt-8 mb-4\">Key Technical Concepts</h3><p class=\"text-slate-300 mb-4\">Refer to the embedded video above for detailed visual explanation and benchmarks.</p>"
        
    if not content_hi:
        content_hi = f"<p class=\"lead text-lg text-slate-300 mb-6\">इस विशेष विश्लेषण में <strong>{channel}</strong> ने आधुनिक तकनीक के प्रमुख सिद्धांतों को विस्तार से समझाया है।</p><h3 class=\"text-xl font-bold text-white mt-8 mb-4\">प्रमुख तकनीकी अवधारणाएं</h3><p class=\"text-slate-300 mb-4\">विस्तृत वीडियो विवरण और बेंचमार्क के लिए ऊपर दिया गया यूट्यूब वीडियो देखें।</p>"
        
    tags = tags or meta.get('tags', ["Tech", "Engineering", "Tutorial"])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(',') if t.strip()]

    new_id = f"post-{str(uuid.uuid4())[:8]}"
    slug = slugify(title_en)
    
    posts = load_posts()
    existing_slugs = [p.get('slug') for p in posts]
    if slug in existing_slugs:
        slug = f"{slug}-{new_id}"

    new_post = {
        "id": new_id,
        "slug": slug,
        "youtube_url": f"https://www.youtube.com/watch?v={video_id}",
        "video_id": video_id,
        "channel_name": channel,
        "published_date": datetime.now().strftime("%Y-%m-%d"),
        "category": category,
        "category_hi": category_hi,
        "tags": tags,
        "reading_time": meta.get('duration_str', '5 min read'),
        "reading_time_hi": meta.get('duration_str', '5 min read').replace('min read', 'मिनट पढ़ें'),
        "thumbnail": meta.get('thumbnail') or f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
        "en": {
            "title": title_en,
            "summary": summary_en,
            "key_takeaways": takeaways_en,
            "content_html": content_en
        },
        "hi": {
            "title": title_hi,
            "summary": summary_hi,
            "key_takeaways": takeaways_hi,
            "content_html": content_hi
        }
    }
    
    posts.insert(0, new_post)
    save_posts(posts)
    print(f"[✓] Successfully published blog post: '{title_en}' (slug: {slug})")
    return new_post

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Add YouTube video to Tech Pulse India bilingual blog")
    parser.add_argument("--url", required=True, help="YouTube video URL")
    parser.add_argument("--title-en", help="English post title")
    parser.add_argument("--title-hi", help="Hindi post title")
    parser.add_argument("--category", default="Smartphones", help="Category name (e.g. Smartphones, Laptops, Smartwatches, Earphones & Audio, Chargers & Power, Desktops & PCs)")
    args = parser.parse_args()
    
    add_blog_post(url=args.url, title_en=args.title_en, title_hi=args.title_hi, category=args.category)
