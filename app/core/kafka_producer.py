"""
F047: Kafka Event Streaming — Producer module.
Topics: expense.created, alert.triggered, project.updated, ai.prediction.ready
"""

import json
import logging
from typing import Any, Optional
from config import settings

logger = logging.getLogger(__name__)

# Lazy-loaded Kafka producer
_producer = None
_kafka_available = False


async def _get_producer():
    """Lazy-initialize the Kafka producer."""
    global _producer, _kafka_available

    if _producer is not None:
        return _producer

    bootstrap = settings.KAFKA_BOOTSTRAP_SERVERS
    if not bootstrap:
        logger.warning("KAFKA_BOOTSTRAP_SERVERS not configured; events will be logged only")
        _kafka_available = False
        return None

    try:
        from aiokafka import AIOKafkaProducer
        _producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap,
            value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
        )
        await _producer.start()
        _kafka_available = True
        logger.info(f"Kafka producer connected to {bootstrap}")
        return _producer
    except Exception as e:
        logger.warning(f"Kafka connection failed: {e}; events will be logged only")
        _kafka_available = False
        return None


async def shutdown_producer():
    """Gracefully shutdown the Kafka producer."""
    global _producer
    if _producer:
        await _producer.stop()
        _producer = None
        logger.info("Kafka producer shut down")


# ── Event Topics ─────────────────────────────────────────────────────────
TOPIC_EXPENSE_CREATED = "expense.created"
TOPIC_ALERT_TRIGGERED = "alert.triggered"
TOPIC_PROJECT_UPDATED = "project.updated"
TOPIC_AI_PREDICTION_READY = "ai.prediction.ready"
TOPIC_EMPLOYEE_FLAGGED = "employee.flagged"
TOPIC_MILESTONE_UPDATED = "milestone.updated"


async def publish_event(topic: str, key: str, data: dict):
    """
    Publish an event to Kafka. Falls back to logging if Kafka is unavailable.
    """
    event = {
        "topic": topic,
        "key": key,
        "data": data,
    }

    producer = await _get_producer()
    if producer and _kafka_available:
        try:
            await producer.send_and_wait(topic, value=data, key=key)
            logger.info(f"Kafka event published: {topic}/{key}")
        except Exception as e:
            logger.error(f"Failed to publish Kafka event: {e}")
            # Fallback: log the event
            logger.info(f"[EVENT-LOG] {topic}/{key}: {json.dumps(data, default=str)}")
    else:
        # Fallback: log the event for debugging
        logger.info(f"[EVENT-LOG] {topic}/{key}: {json.dumps(data, default=str)}")

    # Also push to WebSocket connections if available
    try:
        from app.api.ws.manager import broadcast_event
        await broadcast_event(topic, data)
    except Exception:
        pass

    return event


# ── Convenience Event Publishers ─────────────────────────────────────────

async def emit_expense_created(expense_id: int, project_id: int, amount: float, category: str):
    """Emit event when a new expense is logged."""
    return await publish_event(
        TOPIC_EXPENSE_CREATED,
        key=f"project-{project_id}",
        data={
            "expense_id": expense_id,
            "project_id": project_id,
            "amount": amount,
            "category": category,
            "event_type": "expense_created",
        },
    )


async def emit_alert_triggered(alert_id: int, alert_type: str, severity: str, message: str, entity_id: int = None):
    """Emit event when an alert is triggered."""
    return await publish_event(
        TOPIC_ALERT_TRIGGERED,
        key=f"alert-{alert_type}",
        data={
            "alert_id": alert_id,
            "type": alert_type,
            "severity": severity,
            "message": message,
            "entity_id": entity_id,
            "event_type": "alert_triggered",
        },
    )


async def emit_project_updated(project_id: int, field: str, old_value: Any = None, new_value: Any = None):
    """Emit event when project data changes."""
    return await publish_event(
        TOPIC_PROJECT_UPDATED,
        key=f"project-{project_id}",
        data={
            "project_id": project_id,
            "field": field,
            "old_value": old_value,
            "new_value": new_value,
            "event_type": "project_updated",
        },
    )


async def emit_ai_prediction(project_id: int, model_type: str, prediction: dict):
    """Emit event when an AI prediction is ready."""
    return await publish_event(
        TOPIC_AI_PREDICTION_READY,
        key=f"project-{project_id}",
        data={
            "project_id": project_id,
            "model_type": model_type,
            "prediction": prediction,
            "event_type": "ai_prediction_ready",
        },
    )


async def emit_employee_flagged(employee_id: int, evs_score: float, reason: str):
    """Emit event when an employee is flagged as underperforming."""
    return await publish_event(
        TOPIC_EMPLOYEE_FLAGGED,
        key=f"employee-{employee_id}",
        data={
            "employee_id": employee_id,
            "evs_score": evs_score,
            "reason": reason,
            "event_type": "employee_flagged",
        },
    )
