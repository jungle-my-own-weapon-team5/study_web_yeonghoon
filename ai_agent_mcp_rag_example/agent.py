from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_DIR = Path(__file__).parent


@dataclass(frozen=True)
class RetrievedChunk:
    id: str
    source: str
    text: str
    score: float


class McpClient:
    def __init__(self, server_path: Path):
        self.server_path = server_path

    def rag_search(self, query: str, top_k: int = 3) -> list[RetrievedChunk]:
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "rag_search",
                "arguments": {"query": query, "top_k": top_k},
            },
        }
        response = self._send(request)
        if "error" in response:
            raise RuntimeError(response["error"]["message"])

        content = response["result"]["content"][0]["json"]
        return [
            RetrievedChunk(
                id=item["id"],
                source=item["source"],
                score=float(item["score"]),
                text=item["text"],
            )
            for item in content["results"]
        ]

    def _send(self, request: dict[str, Any]) -> dict[str, Any]:
        process = subprocess.run(
            [sys.executable, str(self.server_path)],
            input=json.dumps(request, ensure_ascii=False) + "\n",
            text=True,
            capture_output=True,
            check=True,
        )
        return json.loads(process.stdout)


class LocalAnswerModel:
    def answer(self, question: str, chunks: list[RetrievedChunk]) -> str:
        if not chunks:
            return "문서에서 관련 근거를 찾지 못했습니다. 질문을 더 구체적으로 바꿔보세요."

        best_sentences: list[str] = []
        question_terms = set(question.lower().split())
        for chunk in chunks:
            sentences = [part.strip() for part in chunk.text.replace("\n", " ").split(".") if part.strip()]
            for sentence in sentences:
                sentence_terms = set(sentence.lower().split())
                if question_terms & sentence_terms:
                    best_sentences.append(sentence)
                    break
            if len(best_sentences) >= 3:
                break

        if not best_sentences:
            best_sentences = [chunks[0].text.replace("\n", " ").strip()]

        citations = ", ".join(f"[{chunk.id}]" for chunk in chunks[:2])
        return f"{' '.join(best_sentences)}. 근거: {citations}"


class Agent:
    def __init__(self, client: McpClient, model: LocalAnswerModel):
        self.client = client
        self.model = model

    def run(self, question: str) -> tuple[str, list[RetrievedChunk]]:
        chunks = self.client.rag_search(question, top_k=3)
        answer = self.model.answer(question, chunks)
        return answer, chunks


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: python3 agent.py "your question"')
        raise SystemExit(2)

    question = " ".join(sys.argv[1:])
    agent = Agent(
        client=McpClient(PROJECT_DIR / "mcp_server.py"),
        model=LocalAnswerModel(),
    )
    answer, chunks = agent.run(question)

    print("Answer:")
    print(answer)
    print()
    print("Sources:")
    for chunk in chunks:
        print(f"- {chunk.id} (score={chunk.score:.4f})")


if __name__ == "__main__":
    main()
