from __future__ import annotations

import re
from typing import Iterable, List


SAMPLE_SENTENCE = "The dogs were running quickly and the runner was better than before."
SENTIMENT_TEXT = "This product is excellent and I absolutely love it!"
CLASSIFICATION_TEXT = "I hate this movie"

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "before",
    "better",
    "but",
    "for",
    "from",
    "has",
    "he",
    "her",
    "his",
    "i",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "our",
    "she",
    "than",
    "that",
    "the",
    "their",
    "there",
    "they",
    "this",
    "to",
    "was",
    "were",
    "we",
    "with",
    "you",
}

POSITIVE_WORDS = {"amazing", "awesome", "excellent", "good", "great", "happy", "love", "positive", "wonderful"}
NEGATIVE_WORDS = {"bad", "awful", "hate", "horrible", "poor", "sad", "terrible", "worst", "negative"}


def tokenize(text: str) -> List[str]:
    return re.findall(r"\b\w+\b", text.lower())


def remove_stopwords(tokens: Iterable[str]) -> List[str]:
    return [token for token in tokens if token not in STOPWORDS]


def stem_word(word: str) -> str:
    for suffix in ("ingly", "edly", "ing", "ed", "ly", "es", "s"):
        if len(word) > len(suffix) + 2 and word.endswith(suffix):
            return word[: -len(suffix)]
    return word


def stem_tokens(tokens: Iterable[str]) -> List[str]:
    try:
        from nltk.stem import PorterStemmer

        stemmer = PorterStemmer()
        return [stemmer.stem(token) for token in tokens]
    except Exception:
        return [stem_word(token) for token in tokens]


def lemmatize_word(word: str) -> str:
    irregulars = {
        "better": "good",
        "best": "good",
        "children": "child",
        "men": "man",
        "mice": "mouse",
        "ran": "run",
        "running": "run",
        "were": "be",
        "was": "be",
    }
    if word in irregulars:
        return irregulars[word]
    if word.endswith("ies") and len(word) > 3:
        return word[:-3] + "y"
    if word.endswith("s") and len(word) > 3:
        return word[:-1]
    return word


def lemmatize_tokens(tokens: Iterable[str]) -> List[str]:
    try:
        from nltk.stem import WordNetLemmatizer

        lemmatizer = WordNetLemmatizer()
        return [lemmatizer.lemmatize(token) for token in tokens]
    except Exception:
        return [lemmatize_word(token) for token in tokens]


def sentiment_label(polarity: float) -> str:
    if polarity > 0.1:
        return "positive"
    if polarity < -0.1:
        return "negative"
    return "neutral"


def analyze_sentiment(text: str) -> dict:
    try:
        from textblob import TextBlob

        sentiment = TextBlob(text).sentiment
        return {"polarity": sentiment.polarity, "subjectivity": sentiment.subjectivity, "label": sentiment_label(sentiment.polarity)}
    except Exception:
        tokens = tokenize(text)
        score = sum(1 for token in tokens if token in POSITIVE_WORDS) - sum(1 for token in tokens if token in NEGATIVE_WORDS)
        polarity = max(-1.0, min(1.0, score / 3.0))
        subjectivity = min(1.0, len(set(tokens)) / max(1, len(tokens)))
        return {"polarity": polarity, "subjectivity": subjectivity, "label": sentiment_label(polarity)}


def classify_text(text: str) -> str:
    try:
        from sklearn.feature_extraction.text import CountVectorizer
        from sklearn.naive_bayes import MultinomialNB

        documents = [
            "I love this movie",
            "This is a fantastic product",
            "I hate this movie",
            "This product is terrible",
            "What a great experience",
            "This is the worst service",
        ]
        labels = ["positive", "positive", "negative", "negative", "positive", "negative"]

        vectorizer = CountVectorizer()
        model = MultinomialNB()
        features = vectorizer.fit_transform(documents)
        model.fit(features, labels)
        return str(model.predict(vectorizer.transform([text]))[0])
    except Exception:
        tokens = tokenize(text)
        positive_hits = sum(1 for token in tokens if token in POSITIVE_WORDS)
        negative_hits = sum(1 for token in tokens if token in NEGATIVE_WORDS)
        if positive_hits > negative_hits:
            return "positive"
        if negative_hits > positive_hits:
            return "negative"
        return "neutral"


def print_section(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def main() -> None:
    tokens = tokenize(SAMPLE_SENTENCE)
    filtered_tokens = remove_stopwords(tokens)
    stemmed_tokens = stem_tokens(filtered_tokens)
    lemmatized_tokens = lemmatize_tokens(tokens)

    print_section("Lab 9: Natural Language Processing")
    print("Here is a simple NLP walkthrough using one sample sentence.")
    print(f"Sentence: {SAMPLE_SENTENCE}")
    print(f"Words after tokenization: {tokens}")
    print(f"After removing stopwords: {filtered_tokens}")
    print(f"After stemming: {stemmed_tokens}")
    print(f"After lemmatization: {lemmatized_tokens}")

    sentiment = analyze_sentiment(SENTIMENT_TEXT)
    print_section("Sentiment Check")
    print(f"Text: {SENTIMENT_TEXT}")
    print(f"Polarity score: {sentiment['polarity']:.3f}")
    print(f"Subjectivity score: {sentiment['subjectivity']:.3f}")
    print(f"Overall feeling: {sentiment['label']}")

    predicted_label = classify_text(CLASSIFICATION_TEXT)
    print_section("Text Classification")
    print(f"Input text: {CLASSIFICATION_TEXT}")
    print(f"Predicted class: {predicted_label}")

    print_section("Where NLP Is Used")
    print("These are a few common real-world uses of NLP:")
    use_cases = [
        "Sentiment Analysis",
        "Chatbots and Virtual Assistants",
        "Machine Translation",
        "Spam Detection",
        "Text Classification and Summarization",
    ]
    for index, use_case in enumerate(use_cases, start=1):
        print(f"{index}. {use_case}")


if __name__ == "__main__":
    main()