"""Private workspace, saved-paper, collection, note, and question models."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import CreatedAt, CreatedUpdatedAt, UUIDPrimaryKey


class User(UUIDPrimaryKey, CreatedUpdatedAt, Base):
    __tablename__ = "users"

    # Authentication, verification, and email uniqueness are intentionally not modeled yet.
    email: Mapped[str] = mapped_column(String(320), nullable=False)

    workspaces: Mapped[list["Workspace"]] = relationship(back_populates="owner")


class Workspace(UUIDPrimaryKey, CreatedUpdatedAt, Base):
    __tablename__ = "workspaces"
    __table_args__ = (Index("ix_workspaces_owner_user_id", "owner_user_id"),)

    owner_user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    owner: Mapped[User] = relationship(back_populates="workspaces")
    saved_papers: Mapped[list["WorkspacePaper"]] = relationship(back_populates="workspace")
    collections: Mapped[list["Collection"]] = relationship(back_populates="workspace")
    notes: Mapped[list["Note"]] = relationship(back_populates="workspace")
    research_questions: Mapped[list["ResearchQuestion"]] = relationship(
        back_populates="workspace"
    )


class WorkspacePaper(Base):
    __tablename__ = "workspace_papers"
    __table_args__ = (
        CheckConstraint(
            "reading_status IN ('to_read', 'reading', 'read')",
            name="reading_status_valid",
        ),
        Index("ix_workspace_papers_paper_id", "paper_id"),
    )

    workspace_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        primary_key=True,
    )
    paper_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("papers.id", ondelete="CASCADE"),
        primary_key=True,
    )
    reading_status: Mapped[str] = mapped_column(String(32), nullable=False, default="to_read")
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    personal_summary: Mapped[str | None] = mapped_column(Text)

    workspace: Mapped[Workspace] = relationship(back_populates="saved_papers")
    paper: Mapped["Paper"] = relationship()
    collection_entries: Mapped[list["CollectionPaper"]] = relationship(
        back_populates="workspace_paper",
        foreign_keys=lambda: [CollectionPaper.workspace_id, CollectionPaper.paper_id],
    )


class Collection(UUIDPrimaryKey, CreatedUpdatedAt, Base):
    __tablename__ = "collections"
    __table_args__ = (
        UniqueConstraint("id", "workspace_id", name="uq_collections_id_workspace"),
        Index("ix_collections_workspace_id", "workspace_id"),
    )

    workspace_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("workspaces.id", ondelete="RESTRICT"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    workspace: Mapped[Workspace] = relationship(back_populates="collections")
    collection_papers: Mapped[list["CollectionPaper"]] = relationship(
        back_populates="collection",
        foreign_keys=lambda: [CollectionPaper.collection_id, CollectionPaper.workspace_id],
        overlaps="collection_entries,workspace_paper",
    )


class CollectionPaper(Base):
    __tablename__ = "collection_papers"
    __table_args__ = (
        ForeignKeyConstraint(
            ["collection_id", "workspace_id"],
            ["collections.id", "collections.workspace_id"],
            name="fk_collection_papers_collection_workspace",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["workspace_id", "paper_id"],
            ["workspace_papers.workspace_id", "workspace_papers.paper_id"],
            name="fk_collection_papers_workspace_paper",
            ondelete="CASCADE",
        ),
        Index("ix_collection_papers_workspace_paper", "workspace_id", "paper_id"),
    )

    collection_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    paper_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    workspace_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    collection: Mapped[Collection] = relationship(
        back_populates="collection_papers",
        foreign_keys=[collection_id, workspace_id],
        overlaps="collection_entries,workspace_paper",
    )
    workspace_paper: Mapped[WorkspacePaper] = relationship(
        back_populates="collection_entries",
        foreign_keys=[workspace_id, paper_id],
        overlaps="collection,collection_papers",
    )


class Note(UUIDPrimaryKey, CreatedUpdatedAt, Base):
    __tablename__ = "notes"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "paper_id"],
            ["workspace_papers.workspace_id", "workspace_papers.paper_id"],
            name="fk_notes_workspace_paper_membership",
            ondelete="RESTRICT",
        ),
        Index("ix_notes_workspace_id", "workspace_id"),
        Index("ix_notes_paper_id", "paper_id"),
    )

    workspace_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("workspaces.id", ondelete="RESTRICT"), nullable=False
    )
    paper_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("papers.id", ondelete="RESTRICT")
    )
    title: Mapped[str | None] = mapped_column(String(512))
    body: Mapped[str] = mapped_column(Text, nullable=False)

    workspace: Mapped[Workspace] = relationship(back_populates="notes")
    paper: Mapped["Paper | None"] = relationship(foreign_keys=[paper_id])


class ResearchQuestion(UUIDPrimaryKey, CreatedUpdatedAt, Base):
    __tablename__ = "research_questions"
    __table_args__ = (
        CheckConstraint(
            "status IN ('open', 'exploring', 'resolved')",
            name="status_valid",
        ),
        Index("ix_research_questions_workspace_id", "workspace_id"),
    )

    workspace_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("workspaces.id", ondelete="RESTRICT"), nullable=False
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="open")

    workspace: Mapped[Workspace] = relationship(back_populates="research_questions")
