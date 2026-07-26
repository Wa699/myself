import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import patch, MagicMock


class TestGenerateAnswer:
    def test_primary_model_success(self):
        """Test primary model returns answer successfully."""
        with patch("llm.PRIMARY_API_KEY", "pk-test"), patch("llm.FALLBACK_API_KEY", ""):
            with patch("llm.OpenAI") as mock_openai:
                mock_client = MagicMock()
                mock_response = MagicMock()
                mock_choice = MagicMock()
                mock_choice.message.content = "张三擅长Java开发"
                mock_response.choices = [mock_choice]
                mock_client.chat.completions.create.return_value = mock_response
                mock_openai.return_value = mock_client

                from llm import generate_answer
                answer, duration_ms = generate_answer(
                    "张三会什么？",
                    ["张三是一名Java高级工程师"]
                )

                assert "张三擅长" in answer or "Java" in answer
                assert duration_ms >= 0

    def test_fallback_on_primary_failure(self):
        """Test fallback model is used when primary fails."""
        with patch("llm.PRIMARY_API_KEY", "pk-test"), patch("llm.FALLBACK_API_KEY", "fk-test"):
            with patch("llm.OpenAI") as mock_openai:
                mock_primary = MagicMock()
                mock_primary.chat.completions.create.side_effect = Exception("timeout")

                mock_fallback = MagicMock()
                mock_response = MagicMock()
                mock_choice = MagicMock()
                mock_choice.message.content = "该候选人擅长后端开发"
                mock_response.choices = [mock_choice]
                mock_fallback.chat.completions.create.return_value = mock_response

                mock_openai.side_effect = [mock_primary, mock_fallback]

                from llm import generate_answer
                answer, duration_ms = generate_answer(
                    "张三的技能是什么？",
                    ["张三有8年Java经验"]
                )

                assert "后端" in answer or "Java" in answer
                assert mock_openai.call_count == 2

    def test_both_models_fail(self):
        """Test RuntimeError when both models fail."""
        with patch("llm.PRIMARY_API_KEY", "pk-test"), patch("llm.FALLBACK_API_KEY", "fk-test"):
            with patch("llm.OpenAI") as mock_openai:
                mock_fail = MagicMock()
                mock_fail.chat.completions.create.side_effect = Exception("error")
                mock_openai.return_value = mock_fail

                from llm import generate_answer
                with pytest.raises(RuntimeError, match="所有模型均不可用"):
                    generate_answer("test?", ["context"])

    def test_no_api_key_configured(self):
        """Test RuntimeError when no API keys are set."""
        with patch("llm.PRIMARY_API_KEY", ""), patch("llm.FALLBACK_API_KEY", ""):
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
