---
name: kafka-setup
description: |
  Use when configuring Apache Kafka as the event backbone for Digital FTE infrastructure.
  Use when setting up topic design, Dapr pub/sub components, consumer groups, or audit trails.
  NOT when building application logic (use dapr-workflow or fastapi-service instead).
---

# Kafka Setup — Event Backbone

## Overview

Apache Kafka serves as the event backbone (L1) for Digital FTE infrastructure. All triggers, status updates, handoffs, and audit events flow through Kafka topics. Accessed via Dapr's Pub/Sub building block — no direct Kafka client code needed.

## Standard Topic Design

| Topic | Purpose | Retention |
|-------|---------|-----------|
| `fte.triggers.inbound` | New task requests | 7 days |
| `fte.sandbox.lifecycle` | Sandbox claim/release events | 30 days |
| `fte.status.updates` | Progress events for dashboards | 30 days |
| `fte.results.completed` | Final outputs for downstream | 90 days |
| `fte.audit.actions` | Immutable action log | 7 years (compliance) |
| `fte.handoffs.{agent}` | Inter-agent task handoffs | 7 days |

## Dapr Pub/Sub Component

```yaml
# dapr/components/pubsub.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "kafka:9092"
    - name: consumerGroup
      value: "digital-fte"
    - name: authType
      value: "none"  # Use SASL in production
```

## Publishing Events (via Dapr)

```python
from dapr.clients import DaprClient

async def publish_status(task_id: str, status: str, details: dict):
    async with DaprClient() as client:
        await client.publish_event(
            pubsub_name="pubsub",
            topic_name="fte.status.updates",
            data={"task_id": task_id, "status": status, **details}
        )

async def publish_audit(action: str, agent: str, data: dict):
    async with DaprClient() as client:
        await client.publish_event(
            pubsub_name="pubsub",
            topic_name="fte.audit.actions",
            data={"action": action, "agent": agent, **data}
        )
```

## Subscribing to Events (via Dapr)

```python
from fastapi import FastAPI
from dapr.ext.fastapi import DaprApp

app = FastAPI()
dapr_app = DaprApp(app)

@dapr_app.subscribe(pubsub="pubsub", topic="fte.triggers.inbound")
async def handle_trigger(event: dict):
    task = event["data"]["task"]
    await start_workflow(task_id=str(uuid.uuid4()), task=task)
```

## Key Rules

1. All events go through Dapr Pub/Sub — never use Kafka client directly
2. Audit topic MUST have 7-year retention for compliance
3. Consumer groups for horizontal scaling
4. No fire-and-forget — always publish completion events
5. Topic naming: `fte.{category}.{subcategory}`
6. Backpressure: Kafka buffers when sandboxes are busy

## Dependencies

```
dapr>=1.14.0
```
