from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    query: str = Field(..., description="User query for the agent workflow")
    stream: bool = Field(default=False, description="Whether to stream the response")

class QueryResponse(BaseModel):
    response: str
    trace_id: str
    confidence_score: float
    turn_count: int

class IngestRequest(BaseModel):
    source_id: str = Field(..., description="Document identifier")
    content: str = Field(..., description="Text content to ingest")
    author: str = Field(default="unknown")
