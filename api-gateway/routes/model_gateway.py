# ==============================
# CHARGEMENT DES BIBLIOTHÈQUES #
# ==============================

from fastapi import APIRouter, Depends, HTTPException, Query
from dependencies import verify_api_key
import httpx
from models.training import TrainingRequest


# Initialisation du routeur
router = APIRouter(prefix="/models", tags=["Models Gateway"])

# Url du service de redirection
MODEL_SERVICE_URL = "http://model_service:8000/training"
MODEL_RESULTS_URL = "http://model_SERVICE:8000/results"


# =======================================
# ROUTE POUR L'ENTRAÎNEMENT DES MODÈLES #
# =======================================

@router.post("/training")
async def start_training(request_data: TrainingRequest, api_key: bool = Depends(verify_api_key)):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(MODEL_SERVICE_URL, json=request_data.model_dump())
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=502, detail=f"Erreur du service : {str(e)}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Impossible de contacter le service modèle : {str(e)}")


# ==========================================
# ROUTE POUR LA RÉCUPÉRATION DES RÉSULTATS #
# ==========================================

@router.get("/results")
async def get_results(library: str = Query(..., description="Pytorch ou tensorflow"), api_key: bool = Depends(verify_api_key)):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(MODEL_RESULTS_URL, params={"library": library})
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=502, detail=f"Erreur du service : {str(e)}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Impossible de contacter le service modèle : {str(e)}")
