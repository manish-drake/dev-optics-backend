from sqlalchemy import (
    Column, Integer, String, Date, DateTime,
    Text, Enum, ForeignKey
)
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship
import enum

from database import Base

class CategoryEnum(str, enum.Enum):
    bug = "bug"
    feature = "feature"
    refactoring = "refactoring"

class App(Base):
    __tablename__ = "apps"
    id          = Column(Integer, primary_key=True, index=True)
    app         = Column(String, unique=True, index=True)
    description = Column(Text)
    tech_stack  = Column(Text)
    github_repo = Column(Text)
    docker_repo = Column(Text)

    versions      = relationship("Version", back_populates="app_obj")
    deployments   = relationship("Deployment", back_populates="app_obj")
    changes       = relationship("Change", back_populates="app_obj")

class Version(Base):
    __tablename__ = "versions"
    id          = Column(Integer, primary_key=True, index=True)
    version     = Column(String, index=True)
    app         = Column(String, ForeignKey("apps.app"))
    dt_started  = Column(Date)
    description = Column(Text)

    app_obj     = relationship("App", back_populates="versions")
    deployments = relationship("Deployment", back_populates="version_obj")
    changes     = relationship("Change", back_populates="version_obj")

class Deployment(Base):
    __tablename__ = "deployments"
    id          = Column(Integer, primary_key=True, index=True)
    dtt_deploy  = Column(DateTime)
    app         = Column(String, ForeignKey("apps.app"))
    version     = Column(String, ForeignKey("versions.version"))
    git_tag     = Column(Text)
    docker_tag  = Column(Text)
    change_log  = Column(Text)

    app_obj     = relationship("App", back_populates="deployments")
    version_obj = relationship("Version", back_populates="deployments")

class Change(Base):
    __tablename__ = "changes"
    id           = Column(Integer, primary_key=True, index=True)
    app          = Column(String, ForeignKey("apps.app"))
    version      = Column(String, ForeignKey("versions.version"))
    dtt_change   = Column(DateTime)
    change_title = Column(Text)
    change_desc  = Column(Text)
    category     = Column(Enum(CategoryEnum))
    dev          = Column(Text)
    image_url    = Column(Text)

    app_obj      = relationship("App", back_populates="changes")
    version_obj  = relationship("Version", back_populates="changes")