# ==============================
# CHARGEMENT DES BIBLIOTHÈQUES #
# ==============================

from fastapi import APIRouter, HTTPException, Query, Depends
from app.models.training import TrainingRequest, TrainingResult
from app.services.kafka_topics_producer import training_order
from app.services.training_results import get_training_results
from typing import List
from auth import TokenData, get_current_user
from db_models.database import SessionLocal, engine
from db_models.models import Outbox
from sqlalchemy.orm import Session
# Initialisation du routeur
router = APIRouter(tags=["Training"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# ===========================================
# ROUTE POUR LE LANCEMENT DE L'ENTRAÎNEMENT #
# ===========================================

@router.post("/training")
async def training(request: TrainingRequest, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    outbox_entry = Outbox(
        event_type="model.training",
        payload={
            "username": current_user.username,
            "dataset": request.dataset,
            "model_version": request.model_version
        }
    )
    db.add(outbox_entry)
    db.commit()
    try:
        result = await training_order(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# ==========================================
# ROUTE POUR LA RÉCUPÉRATION DES RÉSULTATS #
# ==========================================

@router.get("/results", response_model=List[TrainingResult])
async def get_results(
        library: str = Query(..., description="Pytorch ou tensorflow"),
        dataset: str = Query(..., description="Nom du dataset"),
        db: Session = Depends(get_db),
        current_user: TokenData = Depends(get_current_user)):
    outbox_entry = Outbox(
        event_type="model.get_results",
        payload={
            "username": current_user.username,
            "library": library
        }
    )
    db.add(outbox_entry)
    db.commit()
    try:
        results = get_training_results(library, dataset)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))