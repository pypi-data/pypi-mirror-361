import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
from urllib.parse import urlparse

def crawl_url(url: str, save_dir: str = "data"):
    print(f"🌐 Crawling: {url}")

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        res = requests.get(url, timeout=10, headers=headers)
        res.raise_for_status()
    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
        return

    print("✅ Page fetched successfully")

    soup = BeautifulSoup(res.text, "html.parser")

    title = soup.title.string.strip() if soup.title else "No title"
    meta = soup.find("meta", attrs={"name": "description"})
    meta_desc = meta["content"].strip() if meta and meta.get("content") else "No meta description"
    paragraphs = soup.find_all("p")
    text = " ".join(p.text.strip() for p in paragraphs if p.text.strip())

    print(f"📄 Title: {title}")
    print(f"📝 Description: {meta_desc[:60]}...")
    print(f"📑 Paragraphs found: {len(paragraphs)}")

    if not text:
        print("⚠️ No text content found. Skipping save.")
        return

    parsed = urlparse(url)
    filename = parsed.netloc.replace(".", "_") + ".json"

    os.makedirs(save_dir, exist_ok=True)
    filepath = os.path.join(save_dir, filename)

    data = {
        "url": url,
        "title": title,
        "meta_description": meta_desc,
        "text": text,
        "crawled_at": datetime.now().isoformat()
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved: {filepath}")
