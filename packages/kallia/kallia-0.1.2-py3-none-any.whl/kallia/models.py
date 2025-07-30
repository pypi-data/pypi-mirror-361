from typing import List
from pydantic import BaseModel


class DocumentsRequest(BaseModel):
    url: str
    page_number: int = 1
    temperature: float = 0.0
    max_tokens: int = 8192


class Chunk(BaseModel):
    original_text: str
    concise_summary: str


class Document(BaseModel):
    page_number: int
    chunks: List[Chunk] = []


class DocumentsResponse(BaseModel):
    documents: List[Document]
