# ==============================
# CHARGEMENT DES BIBLIOTHÈQUES #
# ==============================

from fastapi import APIRouter, Depends, HTTPException
from dependencies import verify_api_key
import httpx


# Initialisation du routeur
router = APIRouter(prefix="/models", tags=["Models Gateway"])

# Url du service de redirection
MODEL_SERVICE_URL = "http://model_service:8000/training"


# ========================
# ROUTE POUR REDIRECTION #
# ========================
@router.post("/training")
async def start_training(request_data: dict, api_key: bool = Depends(verify_api_key)):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(MODEL_SERVICE_URL, json=request_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=502, detail=f"Erreur du service : {str(e)}")
