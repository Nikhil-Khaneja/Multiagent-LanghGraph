from pydantic import BaseModel, Field

class IngestionEvent(BaseModel):
    """
    Standard schema for a document ingestion event.
    Simulates a message schema one might see on a Kafka topic.
    """
    event_id: str = Field(..., description="Unique identifier for the event")
    source_id: str = Field(..., description="Identifier for the source document")
    content: str = Field(..., description="The raw text content to ingest")
    author: str = Field(default="unknown", description="Author or system originator")
    timestamp: float = Field(..., description="Unix timestamp of event generation")
