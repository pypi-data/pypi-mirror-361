from ..core.document_repository import get_repository


def list_docs(category: str | list[str] | None = None) -> dict[str, object]:
    """
    헥토파이낸셜 연동 문서 목록을 조회합니다.

    Args:
        category (str|list[str]|None): 카테고리명으로 필터링
            - 사용 가능한 카테고리: "PG", "내통장결제", "간편현금결제"
            - 단일: "PG", 다중: ["PG", "내통장결제"]
            - None 시 전체 문서 조회

    Returns:
        dict:
            {
                "문서목록": [
                    {
                        "문서ID": str,
                        "제목": str,
                        "카테고리": str,
                        "파일명": str,
                        "태그": list[str],
                    },
                    ...
                ],
                "안내": str
            }

        ※ 오류 발생 시 {"오류": "..."} 형태로 반환됩니다.
    """
    try:
        repository = get_repository()
        result = repository.list_documents(
            sort_by="id",
            order="asc",
            category=category,
            page=1,
            page_size=50,
        )
        return {
            "문서목록": result["문서목록"],
            "안내": "문서 ID를 참고해 get_docs로 상세 내용을 확인할 수 있습니다.",
        }
    except Exception as e:
        return {
            "오류": f"문서 목록 처리 중 문제가 발생했습니다: {e}"
        }
