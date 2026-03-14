# ================================================
# CONSUMER KAFKA POUR L'ENTRAÎNEMENT DES MODÈLES #
# ================================================


# ==============================
# CHARGEMENT DES BIBLIOTHÈQUES #
# ==============================

from kafka import KafkaConsumer
import json
import time


# ================
# CONSUMER KAFKA #
# ================

def get_consumer(topic_name, group_id):

    while True:
        try:
            consumer = KafkaConsumer(
                topic_name,
                bootstrap_servers=['kafka:9092'],
                group_id=group_id,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='latest',
            )
            print(f"Connection à kafka réussie. Écoute du topic '{topic_name}' avec le group_id '{group_id}'")
            return consumer
        except Exception as e:
            time.sleep(2)
            print("Nouvelle tentative")