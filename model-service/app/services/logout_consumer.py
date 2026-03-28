import datetime
import json
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
import time
import os
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db_models.models import TokenBlacklist
from db_logs.database import SessionLocal, engine
from db_logs.models import Log

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPICS = [
    "user.logout",
]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


while True:
    try:
        consumer = KafkaConsumer(
            *TOPICS,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            group_id='log_service'
        )
        break
    except NoBrokersAvailable:
        print("Kafka non disponible, retry dans 5s...", flush=True)
        time.sleep(5)

for message in consumer:
    topic = message.topic
    payload = message.value
    print(payload)
    db = SessionLocal()
    db.add(payload["token"])
    db.commit()
    db.refresh(payload["token"])
