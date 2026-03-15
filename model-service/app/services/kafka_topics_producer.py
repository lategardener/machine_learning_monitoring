# ==============================
# CHARGEMENT DES BIBLIOTHÈQUES #
# ==============================

from kafka_utils.producer import get_producer, send_message
from app.models.training import TrainingRequest
import asyncio
from functools import partial

_producer = None

def get_producer_instance():
    global _producer
    if _producer is None:
        _producer = get_producer()
    return _producer

# ===================================
# DEMANDE D'ENTRAÎNEMENT DE MODÈLES #
# ===================================

async def training_order(request: TrainingRequest):
    loop = asyncio.get_event_loop()
    producer = await loop.run_in_executor(None, get_producer_instance)
    order_data = request.model_dump()
    send_message(producer, "training_orders", order_data)
    return {"status": "sent", "data": order_data}
