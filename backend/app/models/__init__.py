"""SQLAlchemy models for the documented Research X data foundation."""

from app.models.research import (
    Author,
    AuthorExternalIdentifier,
    MetadataSource,
    Paper,
    PaperAuthor,
    PaperExternalIdentifier,
    PaperMetadataSnapshot,
    PaperReference,
    PaperRelationship,
)
from app.models.workspace import (
    Collection,
    CollectionPaper,
    Note,
    ResearchQuestion,
    User,
    Workspace,
    WorkspacePaper,
)

__all__ = [
    "Author",
    "AuthorExternalIdentifier",
    "Collection",
    "CollectionPaper",
    "MetadataSource",
    "Note",
    "Paper",
    "PaperAuthor",
    "PaperExternalIdentifier",
    "PaperMetadataSnapshot",
    "PaperReference",
    "PaperRelationship",
    "ResearchQuestion",
    "User",
    "Workspace",
    "WorkspacePaper",
]
