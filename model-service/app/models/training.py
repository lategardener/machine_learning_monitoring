# ==============================
# CHARGEMENT DES BIBLIOTHÈQUES #
# ==============================

from pydantic import BaseModel


# ==============================================
# MODÈLE DE DONNÉES POUR LANCER L'ENTRAÎNEMENT #
# ==============================================

class TrainingRequest(BaseModel):
    dataset: str
    model_version: str


# ================================================
# MODÈLE DE DONNÉES POUR RÉCUPÉRER LES RÉSULTATS #
# ================================================

class TrainingResult(BaseModel):
    run_id: str
    library: str
    dataset: str
    model_name: str
    epoch: int
    train_loss: float
    train_accuracy: float
    val_loss: float
    val_accuracy: float
    epoch_duration: float
    cpu_usage: float | None
    ram_usage: float | None
    timestamp: str