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
        length = chunk.word_count
        score = 0.0
        for term in tf:
            df = doc_frequencies.get(term, 0)
            idf = calculate_idf(df, int(params.n))

            numerator = tf[term] * (params.k1 + 1)

            if params.average_doc_length > 0:
                denominator = tf[term] + params.k1 * (1 - params.b + params.b * (length / params.average_doc_length))
            else:
                denominator = tf[term] + params.k1

            if denominator > 0:
                score += idf * (numerator / denominator)
            else:
                score += idf * numerator
        heading_line = chunk.text.splitlines()[0] if chunk.text else ""

        heading_boost = 1.0
        context_boost = 1.0

        if heading_line.startswith('[') and ']' in heading_line:
            context_part = heading_line.split(']')[0] + ']'
            body_part = heading_line.split(']', 1)[1] if ']' in heading_line else ""

            for keyword in keywords:
                if keyword.lower() in context_part.lower():
                    context_boost = 2.0
                if keyword.lower() in body_part.lower():
                    heading_boost = 1.8

        score *= heading_boost * context_boost
        total_tf = sum(tf.values())
        results.append(BM25Result(id=chunk.id, score=score, total_tf=total_tf))
    return results
