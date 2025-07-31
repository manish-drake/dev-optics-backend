from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import database, models, schemas, crud
from fastapi import UploadFile, File
from fastapi.staticfiles import StaticFiles
import os, shutil
from fastapi.middleware.cors import CORSMiddleware

# create database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Dev-Optics API")

# Configure CORS to allow the Angular frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded images from the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Dependency to get DB session per-request
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Apps endpoints ---
@app.get("/apps/", response_model=List[schemas.App])
def read_apps(skip: int=0, limit: int=100, db: Session=Depends(get_db)):
    return crud.get_apps(db, skip, limit)

@app.post("/apps/", response_model=schemas.App)
def create_app(app_in: schemas.AppCreate, db: Session=Depends(get_db)):
    return crud.create_app(db, app_in)

# --- Versions endpoints ---
@app.get("/versions/", response_model=List[schemas.Version])
def read_versions(skip: int=0, limit: int=100, db: Session=Depends(get_db)):
    return crud.get_versions(db, skip, limit)

@app.post("/versions/", response_model=schemas.Version)
def create_version(v_in: schemas.VersionCreate, db: Session=Depends(get_db)):
    return crud.create_version(db, v_in)

# --- Deployments endpoints ---
@app.get("/deployments/", response_model=List[schemas.Deployment])
def read_deployments(skip: int=0, limit: int=100, db: Session=Depends(get_db)):
    return crud.get_deployments(db, skip, limit)

@app.post("/deployments/", response_model=schemas.Deployment)
def create_deployment(d_in: schemas.DeploymentCreate, db: Session=Depends(get_db)):
    return crud.create_deployment(db, d_in)

# --- Changes endpoints ---
@app.get("/changes/", response_model=List[schemas.Change])
def read_changes(skip: int=0, limit: int=100, db: Session=Depends(get_db)):
    return crud.get_changes(db, skip, limit)

@app.post("/changes/", response_model=schemas.Change)
def create_change(c_in: schemas.ChangeCreate, db: Session=Depends(get_db)):
    return crud.create_change(db, c_in)

@app.post("/changes/upload-image/", summary="Upload image for a Change")
async def upload_change_image(file: UploadFile = File(...)):
    """
    Accepts a multipart-encoded file upload and saves it under static/images,
    returning the URL path that can be stored in Change.image_url.
    """
    upload_dir = "static/images"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "url": f"/static/images/{file.filename}"}

# --- Delete endpoints ---

@app.delete("/apps/{app_id}", status_code=204)
def delete_app(app_id: int, db: Session = Depends(get_db)):
    db_app = crud.get_app(db, app_id)
    if not db_app:
        raise HTTPException(status_code=404, detail="App not found")
    crud.delete_app(db, app_id)

@app.delete("/versions/{version_id}", status_code=204)
def delete_version(version_id: int, db: Session = Depends(get_db)):
    db_ver = crud.get_version(db, version_id)
    if not db_ver:
        raise HTTPException(status_code=404, detail="Version not found")
    crud.delete_version(db, version_id)

@app.delete("/deployments/{deployment_id}", status_code=204)
def delete_deployment(deployment_id: int, db: Session = Depends(get_db)):
    db_dep = crud.get_deployment(db, deployment_id)
    if not db_dep:
        raise HTTPException(status_code=404, detail="Deployment not found")
    crud.delete_deployment(db, deployment_id)

@app.delete("/changes/{change_id}", status_code=204)
def delete_change(change_id: int, db: Session = Depends(get_db)):
    db_ch = crud.get_change(db, change_id)
    if not db_ch:
        raise HTTPException(status_code=404, detail="Change not found")
    crud.delete_change(db, change_id)
    
	# --- Update endpoints ---
    
@app.put("/apps/{app_id}", response_model=schemas.App)
def update_app(app_id: int, app_in: schemas.AppCreate, db: Session = Depends(get_db)):
    db_app = crud.get_app(db, app_id)
    if not db_app:
        raise HTTPException(status_code=404, detail="App not found")
    return crud.update_app(db, app_id, app_in)


@app.put("/changes/{change_id}", response_model=schemas.Change)
def update_change(change_id: int, change_in: schemas.ChangeCreate, db: Session = Depends(get_db)):
    db_ch = crud.get_change(db, change_id)
    if not db_ch:
        raise HTTPException(status_code=404, detail="Change not found")
    return crud.update_change(db, change_id, change_in)

@app.put("/versions/{version_id}", response_model=schemas.Version)
def update_version(version_id: int, version_in: schemas.VersionCreate, db: Session = Depends(get_db)):
    db_ver = crud.get_version(db, version_id)
    if not db_ver:
        raise HTTPException(status_code=404, detail="Version not found")
    return crud.update_version(db, version_id, version_in)

@app.put("/deployments/{deployment_id}", response_model=schemas.Deployment)
def update_deployment(deployment_id: int, dep_in: schemas.DeploymentCreate, db: Session = Depends(get_db)):
    db_dep = crud.get_deployment(db, deployment_id)
    if not db_dep:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return crud.update_deployment(db, deployment_id, dep_in)

# --- Milestones endpoints ---
@app.get("/milestones/", response_model=List[schemas.Milestone])
def read_milestones(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_milestones(db, skip, limit)

@app.get("/milestones/{milestone_id}", response_model=schemas.Milestone)
def read_milestone(milestone_id: int, db: Session = Depends(get_db)):
    db_milestone = crud.get_milestone(db, milestone_id)
    if not db_milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    return db_milestone

@app.post("/milestones/", response_model=schemas.Milestone)
def create_milestone(milestone_in: schemas.MilestoneCreate, db: Session = Depends(get_db)):
    return crud.create_milestone(db, milestone_in)

@app.delete("/milestones/{milestone_id}", status_code=204)
def delete_milestone(milestone_id: int, db: Session = Depends(get_db)):
    db_milestone = crud.get_milestone(db, milestone_id)
    if not db_milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    crud.delete_milestone(db, milestone_id)

@app.put("/milestones/{milestone_id}", response_model=schemas.Milestone)
def update_milestone(milestone_id: int, milestone_in: schemas.MilestoneCreate, db: Session = Depends(get_db)):
    db_milestone = crud.get_milestone(db, milestone_id)
    if not db_milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    return crud.update_milestone(db, milestone_id, milestone_in)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",       # "<module>:<app instance>"
        host="0.0.0.0",   # or "127.0.0.1"
        port=1337,        # your chosen port
        reload=True       # dev auto-reload
    )