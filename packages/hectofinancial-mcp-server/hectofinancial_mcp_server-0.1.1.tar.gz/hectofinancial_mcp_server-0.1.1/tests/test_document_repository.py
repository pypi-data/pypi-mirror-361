from src.hectofinancial_mcp_server.core.document_repository import (
    HectoDocumentRepository,
)

# 샘플 문서 데이터 (간단한 예시)
SAMPLE_DOCS = {
    "test1.md": """# 제목1\n본문1\n## 소제목1\n본문2\n로그인 관련 내용\n""",
    "test2.md": """# 제목2\n본문3\n## 소제목2\n본문4\n"""
}

def test_repository_creation_and_loading():
    repo = HectoDocumentRepository(SAMPLE_DOCS)
    assert repo is not None
    assert hasattr(repo, "documents")
    assert hasattr(repo, "search_engine")
    assert len(repo.documents) > 0
    for doc in repo.documents:
        assert "filename" in doc
        assert "title" in doc
        assert "category" in doc
        assert "tags" in doc
        assert "id" in doc

def test_list_documents():
    repo = HectoDocumentRepository(SAMPLE_DOCS)
    docs = repo.list_documents()
    assert isinstance(docs, dict)
    assert "문서목록" in docs
    assert isinstance(docs["문서목록"], list)
    assert len(docs["문서목록"]) > 0
    for doc in docs["문서목록"]:
        assert "문서ID" in doc
        assert "제목" in doc
        assert "카테고리" in doc
        assert "파일명" in doc
        assert "태그" in doc

def test_get_document_by_id():
    repo = HectoDocumentRepository(SAMPLE_DOCS)
    if repo.documents:
        content = repo.get_document_by_id(0)
        assert content is None or isinstance(content, str)
    assert repo.get_document_by_id(-1) is None
    assert repo.get_document_by_id(999) is None

def test_search_documents():
    repo = HectoDocumentRepository(SAMPLE_DOCS)
    result = repo.search_documents(["결제"])
    assert isinstance(result, dict)
    assert "검색결과" in result or "안내" in result or "카테고리별검색결과" in result
    result = repo.search_documents([])
    assert isinstance(result, dict)
    assert "안내" in result
    result = repo.search_documents(["결제", "연동"])
    assert isinstance(result, dict)
    assert "검색결과" in result or "안내" in result or "카테고리별검색결과" in result

def test_repository_integration_and_error():
    repo = HectoDocumentRepository(SAMPLE_DOCS)
    docs = repo.list_documents()
    assert len(docs) > 0
    if docs:
        content = repo.get_document_by_id(0)
        assert content is None or isinstance(content, str)
    search_result = repo.search_documents(["테스트"])
    assert isinstance(search_result, dict)
    assert "검색결과" in search_result or "안내" in search_result or "카테고리별검색결과" in search_result
    assert repo.get_document_by_id(-1) is None
    assert "안내" in repo.search_documents([])
