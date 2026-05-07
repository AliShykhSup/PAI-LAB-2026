from pathlib import Path
import csv
import re
from difflib import SequenceMatcher

from flask import Flask, jsonify, render_template, request


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "hotel_qna.csv"
TOP_K_RESULTS = 4

app = Flask(__name__)


def normalize_text(text: str) -> str:
    cleaned = (text or "").lower().strip()
    cleaned = re.sub(r"[^a-z0-9\s]", " ", cleaned)
    return " ".join(cleaned.split())


def tokenize(text: str) -> set[str]:
    return set(normalize_text(text).split())


def load_qna_data() -> list[dict[str, str]]:
    if DATA_FILE.exists():
        with DATA_FILE.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
    else:
        rows = [
            {
                "question": "What time is check-in available?",
                "answer": "Standard check-in usually starts in the afternoon, around 2:00 PM, but the exact time depends on the hotel policy.",
                "topic": "Hotel",
            },
            {
                "question": "What time is check-out?",
                "answer": "Most hotels ask guests to check out by late morning, often around 11:00 AM, unless late checkout is arranged.",
                "topic": "Hotel",
            },
        ]

    normalized_rows: list[dict[str, str]] = []
    for row in rows:
        question = (row.get("question") or "").strip()
        answer = (row.get("answer") or "").strip()
        topic = (row.get("topic") or "Hotel").strip() or "Hotel"
        if not question or not answer:
            continue

        normalized_rows.append(
            {
                "question": question,
                "answer": answer,
                "topic": topic,
                "question_clean": normalize_text(question),
                "answer_clean": normalize_text(answer),
            }
        )

    if not normalized_rows:
        raise ValueError("The hotel QnA dataset is empty or missing question/answer values.")

    return normalized_rows


QNA_ROWS = load_qna_data()


def search_qna(query: str, top_k: int = TOP_K_RESULTS):
    clean_query = normalize_text(query)
    if not clean_query:
        return []

    query_tokens = tokenize(clean_query)
    scored_rows = []

    for row in QNA_ROWS:
        candidate_text = f"{row['question_clean']} {row['answer_clean']}"
        candidate_tokens = tokenize(candidate_text)
        union_size = len(query_tokens | candidate_tokens) or 1
        overlap_score = len(query_tokens & candidate_tokens) / union_size
        sequence_score = SequenceMatcher(None, clean_query, candidate_text).ratio()
        score = round((0.65 * sequence_score) + (0.35 * overlap_score), 4)
        scored_rows.append((score, row))

    scored_rows.sort(key=lambda item: item[0], reverse=True)

    results = []
    for score, row in scored_rows[:top_k]:
        results.append(
            {
                "question": row["question"],
                "answer": row["answer"],
                "topic": row["topic"],
                "score": score,
            }
        )

    return results


@app.route("/")
def index():
    sample_questions = [row["question"] for row in QNA_ROWS[:6]]
    return render_template(
        "index.html",
        app_title="Task 12 - Hotel QnA Bot",
        subtitle="A lightweight Flask retrieval bot for hotel questions.",
        sample_questions=sample_questions,
        total_questions=len(QNA_ROWS),
    )


@app.route("/search", methods=["POST"])
def search():
    payload = request.get_json(silent=True) or request.form
    query = payload.get("query", "")
    results = search_qna(query)
    best_match = results[0] if results else None

    return jsonify(
        {
            "query": query,
            "results": results,
            "best_match": best_match,
            "count": len(results),
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
