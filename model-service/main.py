# ==============================
# CHARGEMENT DES BIBLIOTHÈQUES #
# ==============================

from fastapi import FastAPI
from routers.training_router import router as training_router


app = FastAPI(title="Service modèle", description="Service de gestion des modèles d'IA")

app.include_router(training_router)

@app.get("/")
async def root():
    return {"message": "Service prêt à l'emploi!"}