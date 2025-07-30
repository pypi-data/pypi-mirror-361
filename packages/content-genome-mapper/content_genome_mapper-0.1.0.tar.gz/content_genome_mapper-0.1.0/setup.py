from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="content_genome_mapper",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "typer",
        "beautifulsoup4",
        "spacy",
        "keybert",
        "bertopic",
        "pandas",
        "matplotlib",
        "wordcloud",
        "jinja2",
        "trafilatura"
    ],
    entry_points={
        "console_scripts": ["genome=content_genome_mapper.cli:app"]
    },
    author="Your Name",
    description="🧬 A tool to reverse-engineer any webpage's semantic structure.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    python_requires=">=3.8"
)
