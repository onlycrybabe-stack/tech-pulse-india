# ⚡ Tech Pulse India — Future Hardware & Gadgets Journal (Bilingual)

A sleek, modern, white-themed tech publication delivering in-depth bilingual technical breakdowns of next-generation smartphones, laptops, smartwatches, earphones, chargers, and desktop hardware in **both English and हिन्दी (Hindi)** with embedded YouTube players.

---

## ✨ Features

- **🌐 Synchronized Bilingual Reading**:
  - Global `[ EN | हिन्दी ]` segmented switch in the top header controlling title, meta, key takeaways, and comprehensive editorial sections simultaneously.
- **🎥 Embedded YouTube Players**:
  - Responsive 16:9 embedded player with official branding and creator credits.
- **⚡ SEO & Rich Snippets Suite**:
  - Dynamic `sitemap.xml` with `xhtml:link` bilingual alternate annotations.
  - Schema.org `TechArticle` and `VideoObject` structured JSON-LD data.
  - Automatic `/robots.txt` and Google Search Console verification support.
- **📬 Clean Contact Link**:
  - Privacy-friendly "Contact Us" / "संपर्क करें" link in the footer.
- **🛡️ Production-Ready**:
  - Pre-configured for deployment on Render via Gunicorn and Render Blueprints.

---

## 🚀 Deploying to Render (render.com)

This repository includes all configuration files needed for a **1-click zero-downtime deployment on Render**:

### Pre-configured Render Files
1. `render.yaml` — Infrastructure Blueprint for automatic service creation
2. `Procfile` — Declares the web worker (`web: gunicorn app:app`)
3. `requirements.txt` — Production packages including `gunicorn`
4. `runtime.txt` & `.python-version` — Pins Python runtime to `3.11.9`
5. `.gitignore` — Excludes cache, logs, and virtual environments

---

### Method A: Connect via GitHub (Recommended)

1. **Push your code to GitHub**:
   - Create a new repository on [GitHub](https://github.com/).
   - Upload or push this folder to your repository.

2. **Deploy on Render**:
   - Log in to your [Render Dashboard](https://dashboard.render.com/).
   - Click **New +** > **Web Service**.
   - Select your GitHub repository.
   - Configure the following settings (if not automatically detected):
     - **Name**: `techpulse-hardware-journal`
     - **Runtime**: `Python`
     - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`
     - **Plan**: `Free`
   - Click **Deploy Web Service**!

---

### Method B: Deploy Using Render Blueprint (1-Click)

1. Push your repository to GitHub.
2. In the Render Dashboard, click **New +** > **Blueprint**.
3. Connect your repository.
4. Render will automatically detect `render.yaml` and configure the build command, start command, health check (`/healthz`), and environment variables.
5. Click **Apply** to launch.

---

## 💻 Local Development

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Server
```bash
python app.py
```
The site runs locally at **[http://localhost:5050](http://localhost:5050)**.

---

## 📁 Repository Structure

```
tech-blog/
├── app.py                 # Flask web application with health check and SEO endpoints
├── youtube_helper.py      # YouTube metadata and transcript extraction utility
├── add_blog_cli.py        # Terminal utility to ingest YouTube videos
├── requirements.txt       # Production dependencies (Flask, gunicorn, yt-dlp, etc.)
├── Procfile               # PaaS worker declaration (web: gunicorn app:app)
├── render.yaml            # Render Blueprint configuration
├── runtime.txt            # Python version specification (python-3.11.9)
├── .python-version        # pyenv / modern buildpack version pin
├── .gitignore             # Git ignore rules
├── data/
│   └── posts.json         # All bilingual blog articles
├── templates/
│   ├── base.html          # Base layout, SVG branding, header switcher, footer
│   ├── index.html         # Homepage 3-column card grid and category filters
│   ├── post.html          # Single article reader with responsive player
│   ├── sitemap.xml        # Dynamic XML sitemap
│   └── robots.txt         # Crawler directive template
└── static/
    └── images/
        └── logo.svg       # Custom cyan/blue vector pulse logo
```
