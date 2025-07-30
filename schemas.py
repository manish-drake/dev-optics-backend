from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Optional
from models import CategoryEnum

class AppBase(BaseModel):
    app: str
    description: Optional[str] = None
    tech_stack: Optional[str] = None
    github_repo: Optional[str] = None
    docker_repo: Optional[str] = None

class AppCreate(AppBase):
    pass

class App(AppBase):
    id: int
    class Config:
        orm_mode = True

class VersionBase(BaseModel):
    version: str
    app: str
    dt_started: date
    description: Optional[str] = None

class VersionCreate(VersionBase):
    pass

class Version(VersionBase):
    id: int
    class Config:
        orm_mode = True

class DeploymentBase(BaseModel):
    dtt_deploy: datetime
    app: str
    version: str
    git_tag: Optional[str] = None
    docker_tag: Optional[str] = None
    change_log: Optional[str] = None

class DeploymentCreate(DeploymentBase):
    pass

class Deployment(DeploymentBase):
    id: int
    class Config:
        orm_mode = True

class ChangeBase(BaseModel):
    app: str
    version: str
    dtt_change: datetime
    change_title: str
    change_desc: str
    category: CategoryEnum
    dev: Optional[str] = None
    image_url: Optional[str] = None

class ChangeCreate(ChangeBase):
    pass

class Change(ChangeBase):
    id: int
    class Config:
        orm_mode = True