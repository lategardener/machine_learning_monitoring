# ==============================
# CHARGEMENT DES BIBLIOTHÈQUES #
# ==============================

from fastapi import FastAPI
from app.routers.training_router import router as training_router
import threading
from services.kafka_metrics_consumer import listen_and_save_metrics
from contextlib import asynccontextmanager


# =================================
# DÉMARRAGE DES PROCESSUS DE FOND #
# =================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    thread = threading.Thread(target=listen_and_save_metrics(), daemon=True)
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