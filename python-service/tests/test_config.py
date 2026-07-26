import os
from unittest.mock import patch
import pytest


class TestConfigDefaults:
    def test_default_primary_model(self):
        with patch.dict(os.environ, {}, clear=True):
            import importlib
            import config
            importlib.reload(config)
            assert config.PRIMARY_MODEL == "deepseek-chat"

    def test_default_fallback_model(self):
        with patch.dict(os.environ, {}, clear=True):
            import importlib
            import config
            importlib.reload(config)
            assert config.FALLBACK_MODEL == "qwen-turbo"

    def test_default_similarity_threshold(self):
        with patch.dict(os.environ, {}, clear=True):
            import importlib
            import config
            importlib.reload(config)
            assert config.SIMILARITY_THRESHOLD == 0.5

    def test_default_chroma_host(self):
        with patch.dict(os.environ, {}, clear=True):
            import importlib
            import config
            importlib.reload(config)
            assert config.CHROMA_HOST == "chroma"

    def test_custom_env_override(self):
        with patch.dict(os.environ, {
            "PRIMARY_MODEL": "custom-model",
            "SIMILARITY_THRESHOLD": "0.7",
        }):
            import importlib
            import config
            importlib.reload(config)
            assert config.PRIMARY_MODEL == "custom-model"
            assert config.SIMILARITY_THRESHOLD == 0.7
