from fastapi import Header, HTTPException, Depends
from config import API_KEY

def verify_api_key(x_api_key: str = Header(...)):
    """
    Vérifie la clé API envoyée dans l'en-tête X-API-KEY.
    """
    if x_api_key.lower() != API_KEY.lower():
        raise HTTPException(status_code=401, detail="Unauthorized: invalid API key")
    return True  # renvoie True si valide