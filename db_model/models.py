from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database import Base
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
    metrique = Column(String, nullable=False)
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