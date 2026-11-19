import os
import json
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, Response
from youtube_helper import extract_video_id, get_video_metadata, get_transcript, slugify

app = Flask(__name__)
POSTS_FILE = os.path.join(os.path.dirname(__file__), 'data', 'posts.json')

# Google Search Console Verification Code
# Set to your Google Search Console token
GSC_VERIFICATION_CODE = os.environ.get(
    'GSC_VERIFICATION_CODE', 
    'cccccdc404ce1a05'
)

@app.context_processor
def inject_seo_globals():
    """Inject dynamic SEO variables into all templates."""
    base_url = request.url_root.rstrip('/')
    return {
        'gsc_code': GSC_VERIFICATION_CODE,
        'site_base_url': base_url,
        'current_year': datetime.now().year,
        'canonical_url': request.base_url
    }

def load_posts():
    """Load all blog posts from the JSON data file."""
    if not os.path.exists(POSTS_FILE):
        return []
    try:
        with open(POSTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading posts: {e}")
        return []

def save_posts(posts):
    """Save posts to the JSON data file."""
    os.makedirs(os.path.dirname(POSTS_FILE), exist_ok=True)
    with open(POSTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

def get_categories():
    """Extract unique categories from all posts."""
    posts = load_posts()
    categories = {}
    for p in posts:
        cat = p.get('category', 'General Tech')
        cat_hi = p.get('category_hi', 'सामान्य टेक')
        if cat not in categories:
            categories[cat] = {
                'name_en': cat,
                'name_hi': cat_hi,
                'slug': slugify(cat),
                'count': 1
            }
        else:
            categories[cat]['count'] += 1
    return list(categories.values())

@app.route('/')
def home():
    all_posts = load_posts()
    categories = get_categories()
    selected_cat = request.args.get('cat', '')
    query = request.args.get('q', '').strip().lower()
    
    filtered = all_posts
    if selected_cat:
        filtered = [p for p in filtered if slugify(p.get('category', '')) == slugify(selected_cat)]
        
    if query:
        filtered = [
            p for p in filtered
            if query in p.get('en', {}).get('title', '').lower()
            or query in p.get('hi', {}).get('title', '').lower()
            or query in p.get('en', {}).get('summary', '').lower()
            or query in p.get('hi', {}).get('summary', '').lower()
            or any(query in t.lower() for t in p.get('tags', []))
        ]
        
    return render_template(
        'index.html',
        posts=filtered,
        categories=categories,
        selected_cat=selected_cat,
        query=query
    )

@app.route('/post/<slug>')
def post_detail(slug):
    posts = load_posts()
    post = next((p for p in posts if p.get('slug') == slug or p.get('id') == slug), None)
    if not post:
        return render_template('404.html'), 404
    
    # Related posts (excluding current)
    related = [p for p in posts if p.get('id') != post.get('id')][:3]
    return render_template('post.html', post=post, related=related)

@app.route('/add-post')
def add_post_page():
    return render_template('add_post.html')

# ==========================================
# SEO & Google Search Console Routes
# ==========================================

@app.route('/sitemap.xml')
def sitemap():
    """Generate dynamic XML sitemap for Google Search Console and crawlers."""
    base_url = request.url_root.rstrip('/')
    posts = load_posts()
    pages = [
        {
            'loc': f"{base_url}/",
            'changefreq': 'daily',
            'priority': '1.0',
            'lastmod': datetime.now().strftime('%Y-%m-%d')
        }
    ]
    for p in posts:
        slug = p.get('slug') or p.get('id')
        pub_date = p.get('published_date', datetime.now().strftime('%Y-%m-%d'))
        pages.append({
            'loc': f"{base_url}/post/{slug}",
            'changefreq': 'weekly',
            'priority': '0.8',
            'lastmod': pub_date
        })
    
    sitemap_xml = render_template('sitemap.xml', pages=pages)
    return Response(sitemap_xml, mimetype='application/xml')

@app.route('/robots.txt')
def robots():
    """Serve robots.txt with sitemap directive for search crawlers."""
    base_url = request.url_root.rstrip('/')
    content = f"""User-agent: *
Allow: /
Disallow: /api/

Sitemap: {base_url}/sitemap.xml
"""
    return Response(content, mimetype='text/plain')

@app.route('/googlecccccdc404ce1a05.html')
def google_exact_verification_file():
    """Exact Google Search Console verification endpoint."""
    return Response("google-site-verification: googlecccccdc404ce1a05.html", mimetype='text/html')

@app.route('/google<token>.html')
def google_verification_file(token):
    """Support Google Search Console HTML verification file upload method."""
    return Response(f"google-site-verification: google{token}.html", mimetype='text/html')

@app.route('/api/preview-youtube', methods=['POST'])
def api_preview_youtube():
    data = request.get_json() or {}
    url = data.get('url', '').strip()
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    video_id = extract_video_id(url)
    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL or ID'}), 400
    
    meta = get_video_metadata(url)
    transcript = get_transcript(video_id)
    meta['transcript_preview'] = transcript[:1500] if transcript else ""
    return jsonify(meta)

@app.route('/api/add-post', methods=['POST'])
def api_add_post():
    data = request.get_json() or {}
    youtube_url = data.get('youtube_url', '').strip()
    video_id = extract_video_id(youtube_url)
    
    if not youtube_url or not video_id:
        return jsonify({'error': 'Valid YouTube URL is required'}), 400

    title_en = data.get('title_en', '').strip() or "Tech Breakthrough Explained"
    title_hi = data.get('title_hi', '').strip() or "नवीनतम टेक विश्लेषण"
    
    summary_en = data.get('summary_en', '').strip()
    summary_hi = data.get('summary_hi', '').strip()
    
    content_html_en = data.get('content_html_en', '').strip()
    content_html_hi = data.get('content_html_hi', '').strip()
    
    takeaways_en = data.get('takeaways_en', [])
    if isinstance(takeaways_en, str):
        takeaways_en = [line.strip() for line in takeaways_en.split('\n') if line.strip()]
        
    takeaways_hi = data.get('takeaways_hi', [])
    if isinstance(takeaways_hi, str):
        takeaways_hi = [line.strip() for line in takeaways_hi.split('\n') if line.strip()]
        
    tags = data.get('tags', ['Tech', 'AI', 'Tutorial'])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(',') if t.strip()]
        
    category = data.get('category', 'Smartphones')
    category_hi = data.get('category_hi', 'स्मार्टफोन')
    
    new_id = f"post-{str(uuid.uuid4())[:8]}"
    slug = slugify(title_en)
    
    # Ensure slug uniqueness
    posts = load_posts()
    existing_slugs = [p.get('slug') for p in posts]
    if slug in existing_slugs:
        slug = f"{slug}-{new_id}"

    reading_time = data.get('reading_time', '5 min read')
    reading_time_hi = data.get('reading_time_hi', '5 मिनट पढ़ें')
    thumbnail = data.get('thumbnail') or f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

    new_post = {
        "id": new_id,
        "slug": slug,
        "youtube_url": f"https://www.youtube.com/watch?v={video_id}",
        "video_id": video_id,
        "channel_name": data.get('channel_name', 'Tech Creator'),
        "published_date": datetime.now().strftime("%Y-%m-%d"),
        "category": category,
        "category_hi": category_hi,
        "tags": tags,
        "reading_time": reading_time,
        "reading_time_hi": reading_time_hi,
        "thumbnail": thumbnail,
        "en": {
            "title": title_en,
            "summary": summary_en,
            "key_takeaways": takeaways_en,
            "content_html": content_html_en
        },
        "hi": {
            "title": title_hi,
            "summary": summary_hi,
            "key_takeaways": takeaways_hi,
            "content_html": content_html_hi
        }
    }
    
    # Add to beginning of posts list
    posts.insert(0, new_post)
    save_posts(posts)
    
    return jsonify({
        'success': True,
        'message': 'Post added successfully!',
        'slug': slug,
        'post': new_post
    })

@app.route('/healthz', methods=['GET'])
def health_check():
    """Health check endpoint for Render and uptime monitoring."""
    return jsonify({
        'status': 'healthy',
        'service': 'Tech Pulse India Hardware Journal',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/api/posts', methods=['GET'])
def api_get_posts():
    return jsonify(load_posts())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    print(f"Starting Tech Pulse India Modern Tech Blog server at http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
