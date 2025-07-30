from sklearn.feature_extraction.text import TfidfVectorizer

def score(text: str, top_n: int = 10):
    vec = TfidfVectorizer(stop_words='english')
    X = vec.fit_transform([text])
    scores = zip(vec.get_feature_names_out(), X.toarray()[0])
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
    return sorted_scores[:top_n]