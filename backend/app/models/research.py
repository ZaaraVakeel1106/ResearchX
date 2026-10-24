"""Bibliographic, author, citation, and metadata provenance models."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import CreatedAt, CreatedUpdatedAt, UUIDPrimaryKey

JSONB_SNAPSHOT = JSON().with_variant(JSONB(), "postgresql")


class Paper(UUIDPrimaryKey, CreatedUpdatedAt, Base):
    __tablename__ = "papers"
    __table_args__ = (
        CheckConstraint(
            "publication_year IS NULL OR publication_year BETWEEN 1 AND 9999",
            name="publication_year_range",
        ),
        CheckConstraint("length(trim(title)) > 0", name="title_not_blank"),
    )

    title: Mapped[str] = mapped_column(Text, nullable=False)
    abstract: Mapped[str | None] = mapped_column(Text)
    publication_year: Mapped[int | None] = mapped_column(SmallInteger)
    publication_date: Mapped[date | None] = mapped_column(Date)
    venue: Mapped[str | None] = mapped_column(String(512))
    publication_type: Mapped[str | None] = mapped_column(String(128))
    language: Mapped[str | None] = mapped_column(String(32))
    landing_page_url: Mapped[str | None] = mapped_column(Text)
    open_access_status: Mapped[str | None] = mapped_column(String(64))

    authorships: Mapped[list["PaperAuthor"]] = relationship(
        back_populates="paper", foreign_keys="PaperAuthor.paper_id"
    )
    external_identifiers: Mapped[list["PaperExternalIdentifier"]] = relationship(
        back_populates="paper"
    )
    metadata_snapshots: Mapped[list["PaperMetadataSnapshot"]] = relationship(
        back_populates="paper"
    )
    outgoing_references: Mapped[list["PaperReference"]] = relationship(
        back_populates="citing_paper",
        foreign_keys="PaperReference.citing_paper_id",
    )
    incoming_references: Mapped[list["PaperReference"]] = relationship(
        back_populates="cited_paper",
        foreign_keys="PaperReference.cited_paper_id",
    )
    outgoing_relationships: Mapped[list["PaperRelationship"]] = relationship(
        back_populates="source_paper",
        foreign_keys="PaperRelationship.source_paper_id",
    )
    incoming_relationships: Mapped[list["PaperRelationship"]] = relationship(
        back_populates="target_paper",
        foreign_keys="PaperRelationship.target_paper_id",
    )


class Author(UUIDPrimaryKey, CreatedAt, Base):
    __tablename__ = "authors"
    __table_args__ = (CheckConstraint("length(trim(display_name)) > 0", name="display_name_not_blank"),)

    display_name: Mapped[str] = mapped_column(String(512), nullable=False)
    normalized_name: Mapped[str | None] = mapped_column(String(512))

    authorships: Mapped[list["PaperAuthor"]] = relationship(back_populates="author")
    external_identifiers: Mapped[list["AuthorExternalIdentifier"]] = relationship(
        back_populates="author"
    )


class PaperAuthor(Base):
    __tablename__ = "paper_authors"
    __table_args__ = (
        UniqueConstraint("paper_id", "author_order", name="uq_paper_authors_paper_order"),
        CheckConstraint("author_order >= 0", name="author_order_nonnegative"),
    )

    paper_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("papers.id", ondelete="CASCADE"),
        primary_key=True,
    )
    author_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("authors.id", ondelete="CASCADE"),
        primary_key=True,
    )
    author_order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_corresponding: Mapped[bool | None] = mapped_column(Boolean)
    source_record_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("metadata_sources.id", ondelete="RESTRICT")
    )

    paper: Mapped[Paper] = relationship(back_populates="authorships")
    author: Mapped[Author] = relationship(back_populates="authorships")
    source_record: Mapped["MetadataSource | None"] = relationship(
        back_populates="author_associations"
    )


class PaperExternalIdentifier(UUIDPrimaryKey, CreatedAt, Base):
    __tablename__ = "paper_external_identifiers"
    __table_args__ = (
        UniqueConstraint(
            "provider", "identifier_type", "normalized_value", name="uq_paper_identifier_normalized"
        ),
        UniqueConstraint(
            "provider", "identifier_type", "identifier_value", name="uq_paper_identifier_original"
        ),
        CheckConstraint("length(trim(provider)) > 0", name="provider_not_blank"),
        CheckConstraint("length(trim(identifier_type)) > 0", name="identifier_type_not_blank"),
        CheckConstraint("length(trim(identifier_value)) > 0", name="identifier_value_not_blank"),
        Index("ix_paper_external_identifiers_paper_id", "paper_id"),
    )

    paper_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("papers.id", ondelete="RESTRICT"), nullable=False
    )
    provider: Mapped[str] = mapped_column(String(128), nullable=False)
    identifier_type: Mapped[str] = mapped_column(String(128), nullable=False)
    identifier_value: Mapped[str] = mapped_column(String(512), nullable=False)
    normalized_value: Mapped[str | None] = mapped_column(String(512))

    paper: Mapped[Paper] = relationship(back_populates="external_identifiers")


class AuthorExternalIdentifier(UUIDPrimaryKey, CreatedAt, Base):
    __tablename__ = "author_external_identifiers"
    __table_args__ = (
        UniqueConstraint(
            "provider", "identifier_type", "normalized_value", name="uq_author_identifier_normalized"
        ),
        UniqueConstraint(
            "provider", "identifier_type", "identifier_value", name="uq_author_identifier_original"
        ),
        CheckConstraint("length(trim(provider)) > 0", name="provider_not_blank"),
        CheckConstraint("length(trim(identifier_type)) > 0", name="identifier_type_not_blank"),
        CheckConstraint("length(trim(identifier_value)) > 0", name="identifier_value_not_blank"),
        Index("ix_author_external_identifiers_author_id", "author_id"),
    )

    author_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("authors.id", ondelete="RESTRICT"), nullable=False
    )
    provider: Mapped[str] = mapped_column(String(128), nullable=False)
    identifier_type: Mapped[str] = mapped_column(String(128), nullable=False)
    identifier_value: Mapped[str] = mapped_column(String(512), nullable=False)
    normalized_value: Mapped[str | None] = mapped_column(String(512))

    author: Mapped[Author] = relationship(back_populates="external_identifiers")


class MetadataSource(UUIDPrimaryKey, CreatedAt, Base):
    __tablename__ = "metadata_sources"
    __table_args__ = (
        CheckConstraint("length(trim(provider_name)) > 0", name="provider_name_not_blank"),
    )

    provider_name: Mapped[str] = mapped_column(String(128), nullable=False)
    provider_record_id: Mapped[str | None] = mapped_column(String(512))
    source_url: Mapped[str | None] = mapped_column(Text)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    license_or_terms_reference: Mapped[str | None] = mapped_column(Text)
    record_checksum: Mapped[str | None] = mapped_column(String(256))

    author_associations: Mapped[list[PaperAuthor]] = relationship(
        back_populates="source_record"
    )
    paper_references: Mapped[list["PaperReference"]] = relationship(
        back_populates="source_record"
    )
    paper_snapshots: Mapped[list["PaperMetadataSnapshot"]] = relationship(
        back_populates="metadata_source"
    )


class PaperReference(UUIDPrimaryKey, CreatedAt, Base):
    __tablename__ = "paper_references"
    __table_args__ = (
        CheckConstraint(
            "resolution_status IN ('resolved', 'unresolved', 'ambiguous')",
            name="resolution_status_valid",
        ),
        CheckConstraint(
            "cited_paper_id IS NULL OR citing_paper_id <> cited_paper_id",
            name="not_self_citing",
        ),
        CheckConstraint(
            "resolution_status <> 'resolved' OR cited_paper_id IS NOT NULL",
            name="resolved_reference_has_target",
        ),
        UniqueConstraint(
            "citing_paper_id", "cited_paper_id", "source_record_id", name="uq_paper_reference_source_target"
        ),
        Index("ix_paper_references_cited_paper_id", "cited_paper_id"),
        Index(
            "uq_paper_reference_source_key",
            "citing_paper_id",
            "source_record_id",
            "external_reference_key",
            unique=True,
            postgresql_where=text("external_reference_key IS NOT NULL"),
            sqlite_where=text("external_reference_key IS NOT NULL"),
        ),
    )

    citing_paper_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("papers.id", ondelete="RESTRICT"), nullable=False
    )
    cited_paper_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("papers.id", ondelete="RESTRICT")
    )
    external_reference_key: Mapped[str | None] = mapped_column(String(512))
    raw_reference_text: Mapped[str | None] = mapped_column(Text)
    resolution_status: Mapped[str] = mapped_column(String(32), nullable=False)
    source_record_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("metadata_sources.id", ondelete="RESTRICT"), nullable=False
    )

    citing_paper: Mapped[Paper] = relationship(
        back_populates="outgoing_references", foreign_keys=[citing_paper_id]
    )
    cited_paper: Mapped[Paper | None] = relationship(
        back_populates="incoming_references", foreign_keys=[cited_paper_id]
    )
    source_record: Mapped[MetadataSource] = relationship(back_populates="paper_references")


class PaperMetadataSnapshot(UUIDPrimaryKey, Base):
    __tablename__ = "paper_metadata_snapshots"
    __table_args__ = (
        UniqueConstraint("paper_id", "metadata_source_id", name="uq_paper_snapshot_source"),
        Index("ix_paper_metadata_snapshots_metadata_source_id", "metadata_source_id"),
    )

    paper_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("papers.id", ondelete="RESTRICT"), nullable=False
    )
    metadata_source_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("metadata_sources.id", ondelete="RESTRICT"), nullable=False
    )
    snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB_SNAPSHOT, nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    paper: Mapped[Paper] = relationship(back_populates="metadata_snapshots")
    metadata_source: Mapped[MetadataSource] = relationship(back_populates="paper_snapshots")


class PaperRelationship(UUIDPrimaryKey, CreatedAt, Base):
    __tablename__ = "paper_relationships"
    __table_args__ = (
        CheckConstraint(
            "relationship_type IN ('SIMILAR_TO', 'INFERRED_RELATED_TO')",
            name="relationship_type_valid",
        ),
        CheckConstraint(
            "origin_type IN ('provider', 'computed', 'ai_inferred')",
            name="origin_type_valid",
        ),
        Index("ix_paper_relationships_source_paper_id", "source_paper_id"),
        Index("ix_paper_relationships_target_paper_id", "target_paper_id"),
    )

    source_paper_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("papers.id", ondelete="RESTRICT"), nullable=False
    )
    target_paper_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("papers.id", ondelete="RESTRICT"), nullable=False
    )
    relationship_type: Mapped[str] = mapped_column(String(32), nullable=False)
    origin_type: Mapped[str] = mapped_column(String(32), nullable=False)
    score: Mapped[Decimal | None] = mapped_column(Numeric)
    explanation: Mapped[str | None] = mapped_column(Text)
    evidence_reference: Mapped[str | None] = mapped_column(Text)
    model_or_method_version: Mapped[str | None] = mapped_column(String(256))

    source_paper: Mapped[Paper] = relationship(
        back_populates="outgoing_relationships", foreign_keys=[source_paper_id]
    )
    target_paper: Mapped[Paper] = relationship(
        back_populates="incoming_relationships", foreign_keys=[target_paper_id]
    )
