# ===============================================
# PRODUCER KAFKA POUR L'ENTRAÎNEMENT DES MODÈLES #
# ===============================================


# ==============================
# CHARGEMENT DES BIBLIOTHÈQUES #
# ==============================

from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
import json
import time


# ================
# PRODUCER KAFKA #
# ================

def get_producer():

    # On s'assure que kafka soit pret
    while True:
        try:

            # Création du topic si ce n'est pas déjà fait
            admin_client = KafkaAdminClient(boostrap_servers=['kafka:9092'])
            topic_name = "training_results"
            try:
                topic = NewTopic(name=topic_name, num_partitions=1, replication_factor=1)
                admin_client.create_topics(new_topics=topic)
                print(f"Topic '{topic_name}' créé avec succès.")
            except TopicAlreadyExistsError:
                print(f"Topic '{topic_name}' existe déjà.")
            finally:
                admin_client.close()

            return KafkaProducer(
                bootstrap_servers=['kafka:9092'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
        except Exception:
            # Le service kafka n'est pas encore pret. Nouvelle tentative après 2s
            time.sleep(2)
            print("Nouvelle tentative")



# ===================
# ENVOI DES DONNÉES #
# ===================

def send_message(producer, topic, data):
    producer.send(topic, data)
    producer.flush()