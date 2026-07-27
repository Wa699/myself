import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import patch, MagicMock


class TestGenerateAnswer:
    def test_primary_model_success(self):
        """Test primary model returns answer successfully."""
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "张三擅长Java开发"}}]
        }
        
        with patch("llm.PRIMARY_API_KEY", "pk-test"), \
             patch("llm.FALLBACK_API_KEY", ""), \
             patch("llm.requests.post", return_value=mock_resp):
            
            from llm import generate_answer
            answer, duration_ms = generate_answer(
                "张三会什么？",
                ["张三是一名Java高级工程师"]
            )
            assert "Java" in answer
            assert duration_ms >= 0

    def test_fallback_on_primary_failure(self):
        """Test fallback model is used when primary fails."""
        mock_fail = MagicMock()
        mock_fail.raise_for_status.side_effect = Exception("timeout")
        
        mock_ok = MagicMock()
        mock_ok.raise_for_status = MagicMock()
        mock_ok.json.return_value = {
            "choices": [{"message": {"content": "该候选人擅长后端开发"}}]
        }
        
        with patch("llm.PRIMARY_API_KEY", "pk-test"), \
             patch("llm.FALLBACK_API_KEY", "fk-test"), \
             patch("llm.requests.post", side_effect=[mock_fail, mock_ok]):
            
            from llm import generate_answer
            answer, duration_ms = generate_answer(
                "张三的技能是什么？",
                ["张三有8年Java经验"]
            )
            assert "后端" in answer or "Java" in answer

    def test_both_models_fail(self):
        """Test RuntimeError when both models fail."""
        mock_fail = MagicMock()
        mock_fail.raise_for_status.side_effect = Exception("error")
        
        with patch("llm.PRIMARY_API_KEY", "pk-test"), \
             patch("llm.FALLBACK_API_KEY", "fk-test"), \
             patch("llm.requests.post", return_value=mock_fail):
            
            from llm import generate_answer
            with pytest.raises(RuntimeError, match="所有模型均不可用"):
                generate_answer("test?", ["context"])

    def test_no_api_key_configured(self):
        """Test RuntimeError when no API keys are set."""
        with patch("llm.PRIMARY_API_KEY", ""), \
             patch("llm.FALLBACK_API_KEY", ""):
            
            from llm import generate_answer
            with pytest.raises(RuntimeError, match="所有模型均不可用"):
                generate_answer("test?", ["context"])


class TestBuildUserPrompt:
    def test_prompt_structure(self):
        """Test prompt includes both context and question."""
        from llm import _build_user_prompt
        prompt = _build_user_prompt("张三会什么？", ["张三擅长Java", "张三有8年经验"])
        assert "候选人资料" in prompt
        assert "张三擅长Java" in prompt
        assert "张三有8年经验" in prompt
        assert "张三会什么？" in prompt
        assert "---" in prompt