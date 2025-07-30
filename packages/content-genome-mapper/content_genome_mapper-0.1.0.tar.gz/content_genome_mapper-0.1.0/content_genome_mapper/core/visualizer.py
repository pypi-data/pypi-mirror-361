from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

def get_topics(text: str, n_topics: int = 5, n_words: int = 5):
    vectorizer = CountVectorizer(stop_words='english')
    X = vectorizer.fit_transform([text])
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
    lda.fit(X)

    words = vectorizer.get_feature_names_out()
    topics = []
    for topic in lda.components_:
        top_words = [words[i] for i in topic.argsort()[-n_words:]]
        topics.append(top_words)
    return topics

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()