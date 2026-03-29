from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Frontend Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="web/static"), name="static")



@app.get("/create")
async def read_create():
    return FileResponse("web/templates/create.html")
@app.get("/home")
async def read_home():
    return FileResponse("web/templates/home.html")

@app.get("/dashboard")
async def read_dashboard():
    return FileResponse("web/templates/dashboard.html")

@app.get("/")
async def read_index():
    return FileResponse("web/templates/home.html")

@app.get("/cgu")
async def read_cgu():
    return FileResponse("web/templates/cgu.html")