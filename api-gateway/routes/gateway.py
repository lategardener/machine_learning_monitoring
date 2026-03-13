from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from dependencies import verify_api_key
import httpx

router = APIRouter(prefix="/users", tags=["Users Gateway"])


USER_SERVICE_URL = "http://user_service:8000/users"

class UserCreate(BaseModel):
    username: str
    password: str


@router.post("/createUser")
async def create_user(user: UserCreate, api_key: bool = Depends(verify_api_key)):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{USER_SERVICE_URL}/createUser",
                json={"username": user.username, "password": user.password}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"Service Erreur: {str(e)}")

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), api_key: bool = Depends(verify_api_key)):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{USER_SERVICE_URL}/login",
                data={"username": form_data.username, "password": form_data.password}
            )
            if response.status_code == 401:
                raise HTTPException(status_code=401, detail="Identifiant incorrect")
                
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"Service Erreur: {str(e)}")

@router.post("/refresh")
async def refresh(request: Request, api_key: bool = Depends(verify_api_key)):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{USER_SERVICE_URL}/refresh",
                headers={"Authorization": auth_header}
            )
            if response.status_code == 401:
                raise HTTPException(status_code=401, detail="token invalide")
                
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"Service Erreur: {str(e)}")

@router.post("/logout")
async def logout(request: Request, api_key: bool = Depends(verify_api_key)):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="NON Autoriser")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{USER_SERVICE_URL}/logout",
                headers={"Authorization": auth_header}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"Service Erreur: {str(e)}")