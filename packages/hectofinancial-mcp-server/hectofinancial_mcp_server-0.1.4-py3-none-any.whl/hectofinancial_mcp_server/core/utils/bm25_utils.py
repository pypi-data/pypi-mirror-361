import math
from typing import Any


def calculate_idf(df: int, n: int) -> float:
    if df <= 0 or n <= 0 or df >= n:
        return 0.0

    numerator = n - df + 0.5
    denominator = df + 0.5

    if denominator <= 0:
        return 0.0

    ratio = numerator / denominator
    if ratio <= 0:
        return 0.0

    return math.log(ratio)


class BM25Params:
    def __init__(self, k1: float = 1.2, b: float = 0.75, average_doc_length: float = 0.0, n: float = 0.0):
        self.k1 = k1
        self.b = b
        self.average_doc_length = float(average_doc_length)
        self.n = float(n)

class BM25Result:
    def __init__(self, id: int, score: float, total_tf: int):
        self.id = id
        self.score = score
        self.total_tf = total_tf


def bm25_score(term_frequencies: dict[int, dict[str, int]], doc_frequencies: dict[str, int],
               chunks: list[Any], params: BM25Params, keywords: list[str]) -> list[BM25Result]:
    results = []

    for chunk in chunks:
        if chunk.id not in term_frequencies:
            continue

        tf = term_frequencies[chunk.id]
        if not tf:
            continue

        length = chunk.word_count
        score = 0.0

        chunk_text_lower = chunk.text.lower()
        matched_keywords = []
        for keyword in keywords:
            if keyword.lower() in chunk_text_lower:
                matched_keywords.append(keyword)

        if not matched_keywords:
            continue

        for keyword in matched_keywords:
            if keyword in tf:
                df = doc_frequencies.get(keyword, 0)
                if df == 0:
                    continue

                idf = calculate_idf(df, int(params.n))
                term_freq = tf[keyword]

                numerator = term_freq * (params.k1 + 1)

                if params.average_doc_length > 0:
                    denominator = term_freq + params.k1 * (1 - params.b + params.b * (length / params.average_doc_length))
                else:
                    denominator = term_freq + params.k1

                if denominator > 0:
                    score += idf * (numerator / denominator)

        match_ratio = len(matched_keywords) / len(keywords)
        if match_ratio >= 0.8:
            score *= 1.5
        elif match_ratio >= 0.5:
            score *= 1.2

        heading_line = chunk.text.splitlines()[0] if chunk.text else ""
        if any(keyword.lower() in heading_line.lower() for keyword in matched_keywords):
            score *= 1.3

        total_tf = sum(tf.values())
        results.append(BM25Result(id=chunk.id, score=score, total_tf=total_tf))

    return results
