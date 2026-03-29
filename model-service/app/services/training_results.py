# ==============================
# CHARGEMENT DES BIBLIOTHÈQUES #
# ==============================

from db_models.database import SessionLocal
from db_models.models import TrainingLog
from app.models.training import TrainingResult
from sqlalchemy import desc
from typing import List


# ==========================================
# RÉCUPÉRATION DES  DONNÉES D'ENTRAÎNEMENT #
# ==========================================

def get_training_results(library: str, dataset: str) -> List[TrainingResult] | None:

    # Ouverture de la session à la base de données
    db = SessionLocal()

    try:
        # On filtre maintenant par 'library' ET par 'dataset' !
        last = db.query(TrainingLog).filter(
            TrainingLog.library == library,
            TrainingLog.dataset == dataset
        ).order_by(desc(TrainingLog.id)).first()

        if not last:
            return []

        epoch = db.query(TrainingLog).filter(TrainingLog.run_id == last.run_id).order_by(desc(TrainingLog.epoch)).all()
        # Formatage des résultats pour l'API
        return [
            TrainingResult(
                run_id=record.run_id,
                library=record.library,
                dataset=record.dataset,
                model_name=record.model_name,
                epoch=record.epoch,
                train_loss=record.train_loss,
                train_accuracy=record.train_accuracy,
                val_loss=record.val_loss,
                val_accuracy=record.val_accuracy,
                epoch_duration=record.epoch_duration,
                cpu_usage=record.cpu_usage,
                ram_usage=record.ram_usage,
                timestamp=record.timestamp,
                status=record.status
            )
            for record in epoch
        ]
    finally:
        # Fermeture de la connexion à la base de données
        db.close()

