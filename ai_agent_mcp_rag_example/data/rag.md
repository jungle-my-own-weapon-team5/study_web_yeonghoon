# RAG

Retrieval-augmented generation, or RAG, grounds an answer in external documents. A RAG system usually loads documents, splits them into chunks, indexes those chunks, retrieves the most relevant chunks for a question, and passes the retrieved context to a model.

RAG는 외부 문서를 검색해서 답변의 근거로 쓰는 패턴이다. 문서를 청크로 나누고, 질문과 관련 있는 청크를 찾은 다음, 그 검색 결과를 모델이나 에이전트에 넘긴다.

RAG is useful when the model should answer from private, local, or frequently changing knowledge. It reduces unsupported guesses because the answer can cite the retrieved chunks.

This example uses a small keyword scoring index instead of a vector database. The architecture stays the same: retrieval first, answer second.
