from typing import Any

from ..core.document_repository import (
    find_doc_meta_by_identifier,
    format_doc_meta,
    get_repository,
)


def get_docs(doc_id: str = "1") -> dict[str, Any]:
    """
    문서 ID(정수 문자열) 또는 파일 경로(문자열)로
    헥토파이낸셜 연동 문서의 원문 전체를 반환합니다.

    Args:
        doc_id (str): 문서 ID (예: "1", "2") 또는 파일 경로 (예: "pg/hecto_financial_pg.md")

    Returns:
        dict: {
            "문서ID": str,       # 요청한 문서 식별자
            "내용": str,         # 마크다운 원문 전체
            "안내": str          # 안내 메시지
        }

        ※ 유효하지 않은 ID/경로일 경우 {"오류": "..."} 형태로 반환
    """
    try:
        repository = get_repository()

        doc_id = str(doc_id)

        if doc_id.isdigit():
            content = repository.get_document_by_id(int(doc_id))
        else:
            doc_meta = find_doc_meta_by_identifier(repository.documents, doc_id)
            content = repository.get_document_by_filename(doc_id) if doc_meta else None

        if not content:
            return {
                "오류": f"문서 ID 또는 경로 '{doc_id}'에 해당하는 문서를 찾을 수 없습니다."
            }

        doc_meta = find_doc_meta_by_identifier(repository.documents, doc_id)
        meta_info = format_doc_meta(doc_meta) if doc_meta else {"문서ID": doc_id}
        meta_info["내용"] = content
        meta_info["안내"] = "해당 문서의 전체 내용을 반환합니다."
        return meta_info

    except Exception as e:
        return {
            "오류": f"문서 조회 중 오류가 발생했습니다: {e}"
        }
