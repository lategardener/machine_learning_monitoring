from sqlalchemy import Column, Integer, String, Float, ForeignKey
from db_models.database import Base
import uuid


class TrainingLog(Base):

    __tablename__ = "training_logs"

    # Identifiant unique
    id = Column(Integer, primary_key=True, index=True)

    # Identifiant d'entraînement
    run_id = Column(String, nullable=False, index=True)

    # Librairie et dataset
    library = Column(String, nullable=False)
    dataset = Column(String, nullable=False)

    # Version du modèle utilisée
    model_name = Column(String, nullable=False)

    # Suivi de métriques
    metric = Column(String, nullable=False)
    epoch = Column(Integer, nullable=False)
    train_loss = Column(Float, nullable=False)
    train_accuracy = Column(Float, nullable=False)
    val_loss = Column(Float, nullable=False)
    val_accuracy = Column(Float, nullable=False)

    # Heure et durée de l'entraînement
    epoch_duration = Column(Float, nullable=False)
    timestamp = Column(String, nullable=False)

    # Ressources utilisées
    cpu_usage = Column(Float, nullable=True)
    ram_usage = Column(Float, nullable=True)


    # État de l'entraînement
    status = Column(String, nullable=False)


class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    expires_at = Column(String)