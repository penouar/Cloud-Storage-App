from pathlib import Path
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.routers.users import router as users_router
from app.routers.folders import router as folders_router
from app.routers.files import router as files_router
from app.models.users import User
from app.models.folders import Folder
from app.models.files import File
from app.models.fileshare import FileShare
from app.models.foldershare import FolderShare



app = FastAPI()

# Allow the frontend to be opened from another origin (e.g. a file or a different dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)
app.include_router(folders_router)
app.include_router(files_router)

@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}


# Frontend: served at http://localhost:8000/  (mounted last so API routes win)
app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="frontend")
