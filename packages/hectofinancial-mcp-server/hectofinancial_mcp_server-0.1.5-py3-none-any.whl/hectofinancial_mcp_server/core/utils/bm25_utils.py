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

        # 헤딩 가중치 향상
        chunk_lines = chunk.text.splitlines() if chunk.text else []
        heading_boost = 1.0

        # 마크다운 헤딩 검사 (첫 3줄 검사)
        for line in chunk_lines[:3]:
            line_stripped = line.strip()
            if line_stripped.startswith('#'):
                # 헤딩 레벨에 따른 가중치 (# > ## > ###)
                heading_level = len(line_stripped) - len(line_stripped.lstrip('#'))
                if heading_level <= 3:
                    if any(keyword.lower() in line_stripped.lower() for keyword in matched_keywords):
                        if heading_level == 1:
                            heading_boost = max(heading_boost, 3.0)  # H1
                        elif heading_level == 2:
                            heading_boost = max(heading_boost, 2.5)  # H2
                        else:
                            heading_boost = max(heading_boost, 2.0)  # H3
                        break

        # 섹션 제목 패턴 검사 ([], > 포함)
        if heading_boost == 1.0:
            for line in chunk_lines[:2]:
                line_stripped = line.strip()
                if (line_stripped.startswith('[') and ']' in line_stripped) or \
                   (line_stripped.startswith('>') and len(line_stripped) > 5):
                    if any(keyword.lower() in line_stripped.lower() for keyword in matched_keywords):
                        heading_boost = max(heading_boost, 1.8)
                        break

        score *= heading_boost

        total_tf = sum(tf.values())
        results.append(BM25Result(id=chunk.id, score=score, total_tf=total_tf))

    return deduplicate_search_results(results, chunks)

def deduplicate_search_results(results: list[BM25Result], chunks: list[Any]) -> list[BM25Result]:
    """검색 결과에서 중복 제거"""
    import hashlib
    from collections import defaultdict

    # 콘텐츠 해시별로 그룹화
    content_groups = defaultdict(list)

    for result in results:
        chunk = chunks[result.id] if result.id < len(chunks) else None
        if chunk:
            # 헤딩 제외하고 본문만 해시 생성
            content_lines = chunk.text.split('\n')
            body_content = '\n'.join(content_lines[1:]) if len(content_lines) > 1 else chunk.text
            content_hash = hashlib.md5(body_content.encode()).hexdigest()
            content_groups[content_hash].append(result)

    # 각 그룹에서 최고 점수만 선택
    deduplicated = []
    for group in content_groups.values():
        if group:
            # 점수가 가장 높은 결과 선택
            best_result = max(group, key=lambda x: x.score)
            deduplicated.append(best_result)

    return deduplicated
