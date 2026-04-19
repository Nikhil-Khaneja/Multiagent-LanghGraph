import asyncio
from typing import List
from server.app.ingestion.events import IngestionEvent
from server.app.observability.logger import logger
from server.app.observability.metrics import metrics_collector
from agentflow.memory.ingestion import ingestion_pipeline

class LocalKafkaAdapter:
    """
    Adapter that simulates a Kafka consumer/producer for document ingestion.
    In a real production system, this would wrap `confluent-kafka` or `aiokafka`.
    """
    def __init__(self):
        self.queue = asyncio.Queue()
        self.is_running = False
        
    async def produce(self, event: IngestionEvent):
        """Simulates producing a message to a Kafka topic."""
        logger.info(f"Producing ingestion event: {event.event_id}")
        await self.queue.put(event)
        
    async def consume_loop(self):
        """Simulates an active consumer polling the topic."""
        self.is_running = True
        logger.info("Started LocalKafkaAdapter consumer loop.")
        
        while self.is_running:
            try:
                # Wait for an event
                event: IngestionEvent = await self.queue.get()
                logger.info(f"Consumed event: {event.event_id}")
                
                # Process via RAG ingestion pipeline
                chunks_stored = ingestion_pipeline.ingest_to_vector_store(
                    text=event.content,
                    source_id=event.source_id,
                    author=event.author
                )
                logger.info(f"Stored {chunks_stored} chunks for event {event.event_id}")
                
                metrics_collector.record_ingestion()
                self.queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in consumer loop: {e}")
                
    def stop(self):
        self.is_running = False

kafka_adapter = LocalKafkaAdapter()
