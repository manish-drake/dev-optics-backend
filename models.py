from sqlalchemy import (
    Column, Integer, String, Date, DateTime,
    Text, Enum, ForeignKey, Boolean
)
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship
import enum

from database import Base

class CategoryEnum(str, enum.Enum):
    tweaks = "tweaks"
    bug = "bug"
    feature = "feature"
    refactoring = "refactoring"
    breaking = "breaking"

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
    delta_maj   = Column(Integer)
    delta_min   = Column(Integer)
    delta_pat   = Column(Integer)
    current     = Column(Boolean)

    app_obj     = relationship("App", back_populates="versions")
    deployments = relationship("Deployment", back_populates="version_obj")
    changes     = relationship("Change", back_populates="version_obj")

class Milestone(Base):
    __tablename__ = "milestones"
    id           = Column(Integer, primary_key=True, index=True)
    milestone    = Column(String, index=True)
    goal         = Column(Text)
    dt_milestone = Column(String)
    proj_ver     = Column(String)
    complete     = Column(Boolean)

    deployments  = relationship("Deployment", back_populates="milestone_obj")

class Deployment(Base):
    __tablename__ = "deployments"
    id          = Column(Integer, primary_key=True, index=True)
    dtt_deploy  = Column(DateTime)
    milestone    = Column(String, ForeignKey("milestones.milestone"))
    app         = Column(String, ForeignKey("apps.app"))
    version     = Column(String, ForeignKey("versions.version"))
    git_tag     = Column(Text)
    docker_tag  = Column(Text)
    change_log  = Column(Text)

    app_obj     = relationship("App", back_populates="deployments")
    version_obj = relationship("Version", back_populates="deployments")
    milestone_obj = relationship("Milestone", back_populates="deployments")

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
    archived     = Column(Boolean, nullable=False, default=False, server_default="0")
    archived_at  = Column(DateTime)

    app_obj      = relationship("App", back_populates="changes")
    version_obj  = relationship("Version", back_populates="changes")
