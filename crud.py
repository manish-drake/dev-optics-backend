from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
import models, schemas

# --- Apps ---
def get_apps(db: Session, skip: int=0, limit: int=100):
    return db.query(models.App).offset(skip).limit(limit).all()

def create_app(db: Session, app: schemas.AppCreate):
    db_obj = models.App(**app.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# You can add get_by_name, update, delete similarly…

# --- Versions ---
def get_versions(db: Session, skip=0, limit=100):
    return db.query(models.Version).offset(skip).limit(limit).all()

def create_version(db: Session, version: schemas.VersionCreate):
    if version.current:
        existing_current = (
            db.query(models.Version)
            .filter(models.Version.app == version.app, models.Version.current.is_(True))
            .first()
        )
        if existing_current:
            raise ValueError("A current version already exists for this app; deactivate it before adding another current version.")
    db_obj = models.Version(**version.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# --- Deployments ---
def get_deployments(db: Session, skip=0, limit=100):
    return db.query(models.Deployment).offset(skip).limit(limit).all()

def create_deployment(db: Session, dep: schemas.DeploymentCreate):
    db_obj = models.Deployment(**dep.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# --- Changes ---
def get_changes(db: Session, skip=0, limit=100, archived: Optional[bool] = None):
    query = db.query(models.Change)
    if archived is not None:
        query = query.filter(models.Change.archived == archived)
    return query.offset(skip).limit(limit).all()


def create_change(db: Session, ch: schemas.ChangeCreate):
    db_obj = models.Change(**ch.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# Fetch changes by version_id with pagination
def get_app_changes_by_version(
    db: Session,
    app: str,
    version: str,
    skip: int = 0,
    limit: int = 100,
    archived: Optional[bool] = None,
):
    query = db.query(models.Change).filter(
        models.Change.version == version,
        models.Change.app == app,
    )
    if archived is not None:
        query = query.filter(models.Change.archived == archived)
    return query.offset(skip).limit(limit).all()

# --- Get by ID helpers ---
def get_app_by_id(db: Session, app_id: int):
    return db.query(models.App).filter(models.App.id == app_id).first()

def get_version_by_id(db: Session, version_id: int):
    return db.query(models.Version).filter(models.Version.id == version_id).first()

# Get version by semver
def get_version_by_semver(db: Session, semver: str):
    return db.query(models.Version).filter(models.Version.version == semver).first()

def get_deployment_by_id(db: Session, deployment_id: int):
    return db.query(models.Deployment).filter(models.Deployment.id == deployment_id).first()

def get_change_by_id(db: Session, change_id: int):
    return db.query(models.Change).filter(models.Change.id == change_id).first()

# --- Delete operations ---

def get_app(db: Session, app_id: int):
    return db.query(models.App).filter(models.App.id == app_id).first()

def delete_app(db: Session, app_id: int):
    db_obj = get_app(db, app_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj

def get_version(db: Session, version_id: int):
    return db.query(models.Version).filter(models.Version.id == version_id).first()

def delete_version(db: Session, version_id: int):
    db_obj = get_version(db, version_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj

def get_deployment(db: Session, deployment_id: int):
    return db.query(models.Deployment).filter(models.Deployment.id == deployment_id).first()

def delete_deployment(db: Session, deployment_id: int):
    db_obj = get_deployment(db, deployment_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj

def get_change(db: Session, change_id: int):
    return db.query(models.Change).filter(models.Change.id == change_id).first()

def delete_change(db: Session, change_id: int):
    db_obj = get_change(db, change_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj

def update_app(db: Session, app_id: int, app_in: schemas.AppCreate):
    db_obj = get_app(db, app_id)
    if not db_obj:
        return None
    for key, value in app_in.dict().items():
        setattr(db_obj, key, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_version(db: Session, version_id: int, version_in: schemas.VersionCreate):
    db_obj = get_version(db, version_id)
    if not db_obj:
        return None
    for key, value in version_in.dict().items():
        setattr(db_obj, key, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_deployment(db: Session, deployment_id: int, dep_in: schemas.DeploymentCreate):
    db_obj = get_deployment(db, deployment_id)
    if not db_obj:
        return None
    for key, value in dep_in.dict().items():
        setattr(db_obj, key, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_change(db: Session, change_id: int, change_in: schemas.ChangeCreate):
    db_obj = get_change(db, change_id)
    if not db_obj:
        return None
    for key, value in change_in.dict().items():
        setattr(db_obj, key, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


# --- Milestones CRUD ---

def archive_changes_for_milestone(db: Session, milestone_name: str) -> int:
    deployments = (
        db.query(models.Deployment.app, models.Deployment.version)
        .filter(models.Deployment.milestone == milestone_name)
        .distinct()
        .all()
    )
    if not deployments:
        return 0

    total_archived = 0
    archive_time = datetime.utcnow()
    version_pairs = set()
    for app, version in deployments:
        version_pairs.add((app, version))
        total_archived += (
            db.query(models.Change)
            .filter(
                models.Change.app == app,
                models.Change.version == version,
                models.Change.archived.is_(False),
            )
            .update(
                {"archived": True, "archived_at": archive_time},
                synchronize_session=False,
            )
        )

    for app, version in version_pairs:
        db.query(models.Version).filter(
            models.Version.app == app,
            models.Version.version == version,
            models.Version.current.is_(True),
        ).update({"current": False}, synchronize_session=False)
    return total_archived

def get_milestones(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Milestone).offset(skip).limit(limit).all()

def create_milestone(db: Session, milestone_in: schemas.MilestoneCreate):
    db_obj = models.Milestone(**milestone_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_milestone(db: Session, milestone_id: int):
    return db.query(models.Milestone).filter(models.Milestone.id == milestone_id).first()

def delete_milestone(db: Session, milestone_id: int):
    db_obj = get_milestone(db, milestone_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj

def update_milestone(db: Session, milestone_id: int, milestone_in: schemas.MilestoneCreate):
    db_obj = get_milestone(db, milestone_id)
    if not db_obj:
        return None
    was_complete = db_obj.complete
    for key, value in milestone_in.dict().items():
        setattr(db_obj, key, value)
    should_archive = (not was_complete) and db_obj.complete
    if should_archive:
        archive_changes_for_milestone(db, db_obj.milestone)
    db.commit()
    db.refresh(db_obj)
    return db_obj
