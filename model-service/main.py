# ==============================
# CHARGEMENT DES BIBLIOTHÈQUES #
# ==============================

from fastapi import FastAPI
from app.routers.training_router import router as training_router
import threading
from app.services.kafka_metrics_consumer import listen_and_save_metrics
from contextlib import asynccontextmanager
from db_models.database import engine, Base
from db_models import models


# =================================
# DÉMARRAGE DES PROCESSUS DE FOND #
# =================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    # Création des tables de la base de données au démarrage
    Base.metadata.create_all(engine)
    thread = threading.Thread(target=listen_and_save_metrics, daemon=True)
    thread.start()

    yield


# ========================
# INITIALISATION FASTAPI #
# ========================

app = FastAPI(title="Service modèle", description="Service de gestion des modèles d'IA", lifespan=lifespan)
app.include_router(training_router)




# ===============
# ROUTE DE TEST #
# ===============

@app.get("/")
async def root():
    return {"message": "Service prêt à l'emploi!"}