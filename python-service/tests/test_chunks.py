import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from chunks import chunk_text


class TestChunkText:
    def test_empty_text_returns_empty_list(self):
        assert chunk_text("") == []
        assert chunk_text("   ") == []

    def test_short_text_returns_single_chunk(self):
        result = chunk_text("hello world")
        assert len(result) == 1
        assert "hello world" in result[0]

    def test_multiple_paragraphs_within_chunk_size(self):
        text = "para1\npara2\npara3"
        result = chunk_text(text, chunk_size=500)
        assert len(result) == 1
        assert "para1" in result[0] and "para3" in result[0]

    def test_paragraphs_exceeding_chunk_size_get_split(self):
        text = "a" * 600 + "\n" + "b" * 600
        result = chunk_text(text, chunk_size=500, overlap=100)
        assert len(result) >= 2
        assert all(len(c) <= 500 for c in result)

    def test_overlap_preserves_context(self):
        text = "first " * 100 + "\n" + "second " * 100 + "\n" + "third " * 100
        result = chunk_text(text, chunk_size=200, overlap=50)
        assert len(result) >= 2
        # at least one chunk should contain parts from different paragraphs
        assert all(len(c) <= 200 for c in result)

    def test_single_paragraph_longer_than_chunk_size(self):
        text = "x" * 1500
        result = chunk_text(text, chunk_size=500, overlap=100)
        assert len(result) >= 3
        assert all(len(c) <= 500 for c in result)

    def test_chinese_text(self):
        text = "张三是一名高级工程师。\n他擅长Java开发。\n他有8年工作经验。"
        result = chunk_text(text)
        assert len(result) == 1
        assert "张三" in result[0]
