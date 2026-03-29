import time
import json
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from db_models.database import SessionLocal
from db_models.models import Outbox

KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"

# Attente que Kafka soit prêt
while True:
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        print("Outbox Worker : Kafka prêt, démarrage du traitement")
        break
    except NoBrokersAvailable:
        print("Kafka non disponible, attente de 5 secondes...")
        time.sleep(5)

def process_outbox():
    db = SessionLocal()
    while True:
        entries = db.query(Outbox).filter(Outbox.published == False).all()
        for entry in entries:
            producer.send(entry.event_type, entry.payload)
            entry.published = True
            db.commit()
            print(f"Publié sur Kafka : {entry.payload}")
        time.sleep(5)

if __name__ == "__main__":
    process_outbox()