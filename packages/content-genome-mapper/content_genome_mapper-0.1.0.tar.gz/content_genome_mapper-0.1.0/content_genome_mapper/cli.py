import typer
from rich.console import Console
from textblob import TextBlob
from content_genome_mapper.core.crawler import crawl_url
from content_genome_mapper.core.extractor import extract, get_entities
from content_genome_mapper.core.salience import score
from content_genome_mapper.core.visualizer import get_topics
from content_genome_mapper.core.comparer import compare_pages
import os
import json

app = typer.Typer(help="🧬 Content Genome Mapper CLI - Crawl, Analyze, Visualize, and Export web content semantically.")
console = Console()

def save_markdown(url: str, title: str, salience_scores, topics, sentiment=None):
    from urllib.parse import urlparse
    parsed = urlparse(url)
    domain = parsed.netloc.replace('.', '_')
    path = f"data/{domain}.md"

    os.makedirs("data", exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# 📌 {title}\n\n")
        f.write(f"**URL**: {url}\n\n")
        if sentiment:
            f.write(f"**Sentiment:** Polarity {sentiment.polarity:.2f}, Subjectivity {sentiment.subjectivity:.2f}\n\n")
        f.write("## 🔍 Top Salient Entities:\n")
        for ent, score in salience_scores[:5]:
            f.write(f"- {ent} ({score:.2f})\n")
        f.write("\n## 🧩 Topics:\n")
        for topic in topics:
            f.write(f"- {topic}\n")

    console.print(f"📄 Report saved to: [green]{path}[/green]")

@app.command()
def crawl(url: str):
    """🌐 Crawl a URL and store raw content for analysis."""
    crawl_url(url)
    console.print("✅ Crawl complete", style="bold green")


@app.command()
def compare(url1: str, url2: str):
    """🔍 Compare two pages by content, keywords, and structure."""
    compare_pages(url1, url2)


@app.command()
def export(format: str = typer.Option("md", help="Choose export format: md / csv / json")):
    """📦 Export results to Markdown / CSV / JSON"""
    console.print(f"📦 Export in format: [cyan]{format}[/cyan]")
    # TODO: Implement actual logic


@app.command()
def analyze(
    url: str,
    sentiment: bool = typer.Option(False, help="Include sentiment analysis"),
    export: str = typer.Option(None, help="Export report format: md / json")
):
    """🧪 Run full analysis: crawl → extract → salience → topics"""
    crawl_url(url)
    text, metadata = extract(url)
    salience_scores = score(text)
    topic_list = get_topics(text)

    # De-duplicate topics
    seen = set()
    unique_topics = []
    for topic in topic_list:
        key = tuple(sorted(topic))
        if key not in seen:
            seen.add(key)
            unique_topics.append(topic)

    console.print("✅ Analysis complete", style="bold green")
    console.print(f"📌 Title: [bold yellow]{metadata.get('title', 'No Title')}[/bold yellow]")

    if sentiment:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        console.print(f"📊 Sentiment → Polarity: [blue]{polarity:.2f}[/blue], Subjectivity: [blue]{subjectivity:.2f}[/blue]")
    else:
        polarity = subjectivity = None

    console.print("🔍 Top Salient Entities:")
    for ent, s in salience_scores[:5]:
        console.print(f"- {ent} ({s:.2f})")

    console.print("🧩 Topics:")
    for topic in unique_topics:
        console.print(f"- {topic}")

    if export == "md":
        save_markdown(url, metadata.get("title", "Untitled"), salience_scores, unique_topics, TextBlob(text).sentiment if sentiment else None)
    elif export == "json":
        from urllib.parse import urlparse
        parsed = urlparse(url)
        path = f"data/{parsed.netloc.replace('.', '_')}.json"
        os.makedirs("data", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "title": metadata.get("title"),
                "salience": salience_scores[:5],
                "topics": unique_topics,
                "sentiment": {
                    "polarity": polarity,
                    "subjectivity": subjectivity
                } if sentiment else None
            }, f, indent=2)
        console.print(f"📄 JSON report saved to: [green]{path}[/green]")


@app.command()
def entities(url: str):
    """📍 Extract named entities"""
    text, _ = extract(url)
    entities = get_entities(text)
    console.print("📍 Named Entities:")
    for ent in entities:
        console.print(f"  - {ent[0]} ({ent[1]})")


@app.command()
def topics(url: str):
    """🧩 Extract topic clusters from content"""
    text, _ = extract(url)
    topic_list = get_topics(text)
    seen = set()
    unique_topics = []
    for topic in topic_list:
        key = tuple(sorted(topic))
        if key not in seen:
            seen.add(key)
            unique_topics.append(topic)

    console.print("🧩 Topics:")
    for topic in unique_topics:
        console.print(f"- {topic}")


@app.command()
def batch(file: str):
    """🧬 Run genome analysis on a batch of URLs"""
    with open(file, "r") as f:
        urls = [line.strip() for line in f if line.strip()]
    for url in urls:
        console.print(f"🔁 Analyzing: {url}")
        analyze(url)


@app.command()
def report(url: str):
    """📝 Generate a final Markdown/HTML report for a URL"""
    console.print(f"📝 Report for: {url}")
    # TODO: Implement report rendering


if __name__ == "__main__":
    app()
