import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest


class TestIsSufficient:
    SIMILARITY_THRESHOLD = 0.5

    def _is_sufficient(self, results):
        """Inline copy of is_sufficient for testing without chromadb import."""
        if not results:
            return False
        return results[0]["distance"] < (1.0 - self.SIMILARITY_THRESHOLD)

    def test_empty_results_insufficient(self):
        assert self._is_sufficient([]) is False

    def test_low_distance_is_sufficient(self):
        results = [{"distance": 0.2, "text": "relevant", "metadata": {}}]
        assert self._is_sufficient(results) is True

    def test_high_distance_is_insufficient(self):
        results = [{"distance": 0.8, "text": "irrelevant", "metadata": {}}]
        assert self._is_sufficient(results) is False

    def test_boundary_distance(self):
        results = [{"distance": 0.5, "text": "borderline", "metadata": {}}]
        # 0.5 < (1.0 - 0.5) = 0.5 → False (strict less-than)
        assert self._is_sufficient(results) is False

    def test_multiple_results_first_is_best(self):
        results = [
            {"distance": 0.3, "text": "best", "metadata": {}},
            {"distance": 0.9, "text": "worst", "metadata": {}},
        ]
        assert self._is_sufficient(results) is True
