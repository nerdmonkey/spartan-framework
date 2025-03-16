from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class TokenUsage(BaseModel):
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int
    completion_tokens_details: Optional[Any] = None
    prompt_tokens_details: Optional[Any] = None


class ContentFilterResults(BaseModel):
    filtered: bool
    severity: str


class PromptFilterResults(BaseModel):
    prompt_index: int
    content_filter_results: Dict[str, ContentFilterResults]


class Metadata(BaseModel):
    token_usage: TokenUsage
    model_name: str
    system_fingerprint: str
    prompt_filter_results: List[PromptFilterResults]
    finish_reason: str
    logprobs: Optional[Any] = None
    content_filter_results: Dict[str, ContentFilterResults]


class ResponseMetadata(BaseModel):
    model_config = ConfigDict(extra="allow")
    content: Any
    metadata: Metadata


class QueryResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    status_code: int = Field(default=200, alias="statusCode")
    response: ResponseMetadata
