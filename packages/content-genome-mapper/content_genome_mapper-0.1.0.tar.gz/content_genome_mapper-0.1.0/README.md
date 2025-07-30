# 🧬 Content Genome Mapper CLI

A command-line tool to **crawl, analyze, visualize, and export semantic content data** from web pages — ideal for SEO, content analysis, and research.

---

## Features

- 🌐 Crawl web pages and store raw content  
- 🔍 Extract salient entities and score their importance  
- 🧩 Identify topic clusters from content  
- 📊 Optional sentiment analysis (polarity & subjectivity)  
- 📍 Extract named entities  
- 🔄 Compare content and structure of two URLs  
- 🧬 Batch process multiple URLs from a file  
- 📦 Export analysis reports in Markdown and JSON formats  

---

## Installation

```bash
pip install content_genome_mapper
```

*Replace with your package install instructions if different.*

---

## Usage

Use the CLI tool `genome` with the following commands:

### Crawl a URL

```bash
genome crawl https://example.com
```

### Analyze a URL (optional sentiment & export)

```bash
genome analyze https://example.com --sentiment --export md
```

### Extract named entities

```bash
genome entities https://example.com
```

### Extract topics

```bash
genome topics https://example.com
```

### Compare two URLs

```bash
genome compare https://site1.com https://site2.com
```

### Batch analyze URLs from a text file

```bash
genome batch urls.txt
```

---

## Export Formats

- Markdown (`md`) — saves a nicely formatted report  
- JSON (`json`) — structured report data  
- CSV — planned for future release  

Reports are saved in the `data/` folder with filenames based on the domain.

---

## Example Markdown Report

```markdown
# 📌 Example Page Title

**URL**: https://example.com

**Sentiment:** Polarity 0.12, Subjectivity 0.34

## 🔍 Top Salient Entities:
- Entity1 (0.92)
- Entity2 (0.75)

## 🧩 Topics:
- Topic cluster 1
- Topic cluster 2
```

---

## Dependencies

- [Typer](https://typer.tiangolo.com/) — for CLI  
- [Rich](https://rich.readthedocs.io/) — for console output  
- [TextBlob](https://textblob.readthedocs.io/) — for sentiment analysis  
- Internal modules: `content_genome_mapper.core.*`

---

## Contributing

Feel free to submit issues or pull requests to improve the tool!

---

## License

MIT License © Amal ALexander

---

## Contact

For questions or support, contact: amalalex95@gmail.com

## Github Repo
Homepage: https://github.com/amal-alexander
Repository: https://github.com/amal-alexander?tab=repositories
