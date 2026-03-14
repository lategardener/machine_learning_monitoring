# ==============================
# CHARGEMENT DES BIBLIOTHÈQUES #
# ==============================

from fastapi import APIRouter, HTTPException
from models.training import TrainingRequest
from services.kafka_service import training_order



# Initialisation du routeur
router = APIRouter(tags=["Training"])

# ===========================================
# ROUTE POUR LE LANCEMENT DE L'ENTRAÎNEMENT #
# ===========================================

@router.post("/training")
async def training(request: TrainingRequest):
    try:
        result = training_order(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

