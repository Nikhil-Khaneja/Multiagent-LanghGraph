# User Acceptance Testing (UAT) Plan

## Overview
This document outlines the User Acceptance Testing scenarios for the Multi-Agent LLM Backend. The goal is to verify that the core functionalities (API endpoints, RAG ingestion, Agent Workflow, Guardrails, and Observability) operate according to the design specifications.

## Test Scenarios

### Scenario 1: System Health & Availability
- **Objective**: Verify that the FastAPI server starts and exposes its endpoints.
- **Action**: Send a `GET` request to `/api/v1/health`.
- **Expected Result**: HTTP 200 OK with `{"status": "ok", "version": "1.0.0"}`.

### Scenario 2: Webapp Frontend Delivery
- **Objective**: Verify that the static frontend dashboard is served correctly.
- **Action**: Send a `GET` request to `/`.
- **Expected Result**: HTTP 200 OK containing the HTML content of the dashboard.

### Scenario 3: Document Ingestion (Event-Driven)
- **Objective**: Verify that documents can be queued for ingestion into the RAG vector store.
- **Action**: Send a `POST` request to `/api/v1/ingest` with a `source_id` and `content`.
- **Expected Result**: HTTP 200 OK returning an `event_id`. The background Kafka adapter should process the event without throwing exceptions.

### Scenario 4: Standard Agent Query (Happy Path)
- **Objective**: Verify that a query triggers the LangGraph workflow and returns a final response.
- **Action**: Send a `POST` request to `/api/v1/query` with `{"query": "What is the document about?", "stream": false}`.
- **Expected Result**: HTTP 200 OK returning `response`, `trace_id`, `confidence_score`, and `turn_count`.

### Scenario 5: Guardrails & Fallback (Simulated)
- **Objective**: Verify that the guardrails node properly catches low-confidence results and triggers a retry loop.
- **Action**: Send a `POST` request to `/api/v1/query` specifically designed to trigger low confidence or invalid JSON from the analyzer.
- **Expected Result**: The workflow should reflect a higher `turn_count` (e.g., > 3) indicating a loop occurred, and eventually return a graceful failure or corrected response.

### Scenario 6: Observability Metrics Update
- **Objective**: Verify that metrics are updated after requests and ingestions.
- **Action**: Send a `GET` request to `/api/v1/metrics`.
- **Expected Result**: HTTP 200 OK returning metrics where `total_requests` > 0 and `total_ingested_events` > 0.
