from content_genome_mapper.core import extractor, visualizer

def compare_pages(url1: str, url2: str):
    text1, _ = extractor.extract(url1)
    text2, _ = extractor.extract(url2)
    topics1 = set(tuple(t) for t in visualizer.get_topics(text1))
    topics2 = set(tuple(t) for t in visualizer.get_topics(text2))
    overlap = topics1 & topics2
    print(f"🔗 Common Topics: {len(overlap)}")
    for topic in overlap:
        print(f"- {' | '.join(topic)}")