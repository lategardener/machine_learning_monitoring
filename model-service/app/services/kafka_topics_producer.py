# ==============================
# CHARGEMENT DES BIBLIOTHÈQUES #
# ==============================

from kafka.utils.producer import get_producer, send_message
from models.training import TrainingRequest


# Récupération du producer kafka pour l'envoi des ordres d'entraînement
producer = get_producer()


# ===================================
# DEMANDE D'ENTRAÎNEMENT DE MODÈLES #
# ===================================

def training_order(request : TrainingRequest):
    order_data = request.model_dump()

    send_message(producer, "training_orders", order_data)
    return {"status": "sent", "data": order_data}