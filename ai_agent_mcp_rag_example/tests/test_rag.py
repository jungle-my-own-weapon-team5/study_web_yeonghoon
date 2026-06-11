from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rag import RagIndex


class RagIndexTest(unittest.TestCase):
    def test_search_returns_relevant_mcp_chunk(self) -> None:
        index = RagIndex.from_directory(Path(__file__).resolve().parents[1] / "data")

        results = index.search("What does MCP do for an agent?", top_k=1)

        self.assertEqual(len(results), 1)
        self.assertIn("mcp", results[0].chunk.source.lower())
        self.assertGreater(results[0].score, 0)


if __name__ == "__main__":
    unittest.main()
