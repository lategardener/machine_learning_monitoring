# ==============================
# CHARGEMENT DES BIBLIOTHÈQUES #
# ==============================

from fastapi import APIRouter, HTTPException, Query
from app.models.training import TrainingRequest, TrainingResult
from app.services.kafka_topics_producer import training_order
from app.services.training_results import get_training_results
from typing import List


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



# ==========================================
# ROUTE POUR LA RÉCUPÉRATION DES RÉSULTATS #
# ==========================================

@router.get("/results", response_model=List[TrainingResult])
async def get_results(library: str = Query(..., description="Pytorch ou tensorflow")):
    try:
        results = get_training_results(library)
        if results is None:
            raise HTTPException(status_code=404, detail=f"Aucun résultat trouvé pour la librairie : {library}")
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))