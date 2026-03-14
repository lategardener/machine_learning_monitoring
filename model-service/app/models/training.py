# ==============================
# CHARGEMENT DES BIBLIOTHÈQUES #
# ==============================

from pydantic import BaseModel


# ===================
# MODÈLE DE DONNÉES #
# ===================

class TrainingRequest(BaseModel):
    dataset: str
    model_version: str