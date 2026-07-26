import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from models import ChatRequest, ChatResponse, Citation, ImportRequest
from pydantic import ValidationError


class TestChatRequest:
    def test_valid_request(self):
        req = ChatRequest(question="张三的技能是什么？")
        assert req.question == "张三的技能是什么？"

    def test_missing_question_raises_error(self):
        with pytest.raises(ValidationError):
            ChatRequest()

    def test_empty_question_is_allowed(self):
        req = ChatRequest(question="")
        assert req.question == ""


class TestCitation:
    def test_create_citation(self):
        c = Citation(title="项目经历", category="项目", excerpt="电商平台微服务改造")
        assert c.title == "项目经历"
        assert c.category == "项目"


class TestChatResponse:
    def test_success_response(self):
        resp = ChatResponse(
            answer="张三擅长Java",
            citations=[
                Citation(title="技能", category="技能", excerpt="Java")
            ],
            evidence_sufficient=True,
            duration_ms=1500
        )
        assert resp.answer == "张三擅长Java"
        assert len(resp.citations) == 1
        assert resp.evidence_sufficient is True

    def test_insufficient_data_response(self):
        resp = ChatResponse(
            answer="根据已有资料，无法确认该信息",
            citations=[],
            evidence_sufficient=False,
            duration_ms=200
        )
        assert resp.citations == []
        assert resp.evidence_sufficient is False

    def test_missing_field_raises_error(self):
        with pytest.raises(ValidationError):
            ChatResponse(answer="test")


class TestImportRequest:
    def test_valid_request(self):
        req = ImportRequest(file_path="/data/resume.json")
        assert req.file_path == "/data/resume.json"
