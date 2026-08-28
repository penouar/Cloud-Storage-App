from fastapi import FastAPI, Depends
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

app.include_router(users_router)
app.include_router(folders_router)
app.include_router(files_router)

@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}
