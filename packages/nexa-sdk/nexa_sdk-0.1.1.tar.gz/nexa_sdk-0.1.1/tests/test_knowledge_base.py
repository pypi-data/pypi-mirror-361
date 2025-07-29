import pytest
from unittest.mock import MagicMock
from nexa_sdk.knowledge_base import KnowledgeBaseAPI, KnowledgeBase, CreateKnowledgeBaseDto, DeleteKnowledgeBasesDto, UploadToBolnaKnowledgeBaseDto, PaginatedKnowledgeBase, PaginationMeta

class DummyClient:
    def request(self, method, path, **kwargs):
        if method == "POST" and path == "/knowledge-base":
            return {"id": 1, "org_id": 1, "agent_id": 1, "name": "KB1"}
        if method == "DELETE" and path == "/knowledge-base":
            return {"deleted": True}
        if method == "POST" and path.startswith("/knowledge-base/surr/upload/"):
            return None
        if method == "DELETE" and path.startswith("/knowledge-base/surr/delete/"):
            return {"deleted": True}
        if path == "/knowledge-base":
            # Paginated response
            return {
                "items": [{"id": 1, "org_id": 1, "agent_id": 1, "name": "KB1"}],
                "meta": {"totalItems": 1, "itemsPerPage": 10, "totalPages": 1, "currentPage": 1}
            }
        if path.startswith("/knowledge-base/"):
            return {"id": 1, "org_id": 1, "agent_id": 1, "name": "KB1"}
        return {}

def test_list_knowledge_bases():
    api = KnowledgeBaseAPI(DummyClient())
    result = api.list_knowledge_bases("org1")
    if isinstance(result, list):
        assert isinstance(result[0], KnowledgeBase)
    else:
        assert isinstance(result, PaginatedKnowledgeBase)
        assert isinstance(result.items[0], KnowledgeBase)

def test_get_knowledge_base():
    api = KnowledgeBaseAPI(DummyClient())
    kb = api.get_knowledge_base(1)
    assert isinstance(kb, KnowledgeBase)

def test_create_knowledge_base():
    api = KnowledgeBaseAPI(DummyClient())
    dto = CreateKnowledgeBaseDto(agent_id=1, name="KB1")
    kb = api.create_knowledge_base(dto, "org1")
    assert isinstance(kb, KnowledgeBase) 

def test_list_knowledge_bases_paginated():
    api = KnowledgeBaseAPI(DummyClient())
    result = api.list_knowledge_bases("org1", page=1, limit=10)
    assert isinstance(result, PaginatedKnowledgeBase)
    assert isinstance(result.items[0], KnowledgeBase)
    assert isinstance(result.meta, PaginationMeta)

def test_delete_multiple_knowledge_bases():
    api = KnowledgeBaseAPI(DummyClient())
    dto = DeleteKnowledgeBasesDto(agent_id=1, knowledge_base_ids=[1])
    resp = api.delete_multiple_knowledge_bases(dto)
    assert resp["deleted"] is True

def test_upload_document():
    api = KnowledgeBaseAPI(DummyClient())
    dto = UploadToBolnaKnowledgeBaseDto(name="doc")
    # Should not raise
    assert api.upload_document(1, dto) is None

def test_delete_from_vector_db():
    api = KnowledgeBaseAPI(DummyClient())
    resp = api.delete_from_vector_db("vector1")
    assert resp["deleted"] is True 

def test_list_knowledge_bases_list():
    class ListClient:
        def request(self, method, path, **kwargs):
            return [{"id": 1, "org_id": 1, "agent_id": 1, "name": "KB1"}]
    api = KnowledgeBaseAPI(ListClient())
    result = api.list_knowledge_bases("org1")
    assert isinstance(result, list)
    assert isinstance(result[0], KnowledgeBase)

def test_update_knowledge_base():
    class UpdateClient:
        def request(self, method, path, **kwargs):
            return {"id": 1, "org_id": 1, "agent_id": 1, "name": "KB1"}
    api = KnowledgeBaseAPI(UpdateClient())
    resp = api.update_knowledge_base(1, {})
    assert isinstance(resp, KnowledgeBase)

def test_delete_knowledge_base():
    class DeleteClient:
        def request(self, method, path, **kwargs):
            return None
    api = KnowledgeBaseAPI(DeleteClient())
    assert api.delete_knowledge_base(1) is None 