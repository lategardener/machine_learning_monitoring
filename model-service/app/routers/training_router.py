# ==============================
# CHARGEMENT DES BIBLIOTHÈQUES #
# ==============================

from fastapi import APIRouter, HTTPException
from app.models.training import TrainingRequest
from app.services.kafka_topics_producer import training_order



# Initialisation du routeur
router = APIRouter(tags=["Training"])

# ===========================================
# ROUTE POUR LE LANCEMENT DE L'ENTRAÎNEMENT #
# ===========================================

@router.post("/training")
async def training(request: TrainingRequest):
    try:
        result = await training_order(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

