import datetime
import json
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
import time
import os
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db_logs.database import SessionLocal, engine
from db_logs.models import Log

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPICS = [
    "user.created",
    "user.login",
    "user.logout",
]
Log.metadata.create_all(bind=engine)

class LogCreate(BaseModel):
    date: str
    topic: str
    content: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_log(log: LogCreate, db: Session):
    db_log = Log(
        date=log.date,
        topic=log.topic,
        content=json.dumps(log.content)
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

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

print("Notification Service démarré, en attente d'événements...", flush=True)

for message in consumer:
    topic = message.topic
    payload = message.value
    print(payload)
    if topic == "user.created":
        log = Log(date=datetime.datetime.today().isoformat(), topic=topic, content=payload)
        db = SessionLocal()
        create_log(log,db)
        print("l'utilisateur " + payload['username'] + " à bien était créé")
    if topic == "user.login":
        log = Log(date=datetime.datetime.today().isoformat(), topic=topic, content=payload)
        db = SessionLocal()
        create_log(log,db)
        print("l'utilisateur " + payload['username'] + " s'est connecté")
    if topic == "user.logout":
        log = Log(date=datetime.datetime.today().isoformat(), topic=topic, content=payload)
        db = SessionLocal()
        create_log(log,db)
        print("l'utilisateur " + payload['username'] + " s'est déconnecter")