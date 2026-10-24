from datetime import datetime, timezone
from pathlib import Path

import pytest
from alembic import command
from alembic.migration import MigrationContext
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from sqlalchemy import create_engine, event, inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, configure_mappers

from app.db.base import Base
from app.models import (
    Author,
    Collection,
    CollectionPaper,
    MetadataSource,
    Note,
    Paper,
    PaperAuthor,
    PaperExternalIdentifier,
    PaperMetadataSnapshot,
    PaperReference,
    PaperRelationship,
    ResearchQuestion,
    User,
    Workspace,
    WorkspacePaper,
)

BACKEND_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def db_engine():
    engine = create_engine("sqlite://")

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _record):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    configure_mappers()
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def session(db_engine):
    with Session(db_engine) as db_session:
        yield db_session
        db_session.rollback()


def add_paper(session: Session, title: str) -> Paper:
    paper = Paper(title=title)
    session.add(paper)
    session.flush()
    return paper


def add_workspace(session: Session) -> Workspace:
    user = User(email="placeholder@example.invalid")
    workspace = Workspace(owner=user, name="Test workspace")
    session.add(workspace)
    session.flush()
    return workspace


def test_paper_author_relationship_and_author_order_constraint(session: Session) -> None:
    paper = add_paper(session, "A research paper")
    first = Author(display_name="A. Researcher")
    second = Author(display_name="B. Researcher")
    session.add_all([first, second])
    session.flush()
    paper.authorships.extend(
        [
            PaperAuthor(author=first, author_order=0),
            PaperAuthor(author=second, author_order=1),
        ]
    )
    session.flush()

    assert [authorship.author.display_name for authorship in paper.authorships] == [
        "A. Researcher",
        "B. Researcher",
    ]

    third = Author(display_name="C. Researcher")
    session.add(third)
    session.flush()
    session.add(PaperAuthor(paper_id=paper.id, author_id=third.id, author_order=1))
    with pytest.raises(IntegrityError):
        session.flush()
    session.rollback()


def test_identifier_original_and_normalized_values_are_unique(session: Session) -> None:
    paper = add_paper(session, "A research paper")
    identifier = PaperExternalIdentifier(
        paper=paper,
        provider="crossref",
        identifier_type="doi",
        identifier_value="10.1234/example",
        normalized_value="10.1234/example",
    )
    session.add(identifier)
    session.flush()
    session.add(
        PaperExternalIdentifier(
            paper=paper,
            provider="crossref",
            identifier_type="doi",
            identifier_value="10.1234/example",
            normalized_value="10.1234/example",
        )
    )
    with pytest.raises(IntegrityError):
        session.flush()
    session.rollback()


def test_citations_are_distinct_from_non_citation_relationships(session: Session) -> None:
    citing = add_paper(session, "Citing paper")
    cited = add_paper(session, "Cited paper")
    source = MetadataSource(
        provider_name="fixture provider",
        retrieved_at=datetime.now(timezone.utc),
    )
    session.add(source)
    session.flush()

    reference = PaperReference(
        citing_paper=citing,
        cited_paper=cited,
        resolution_status="resolved",
        source_record=source,
    )
    similarity = PaperRelationship(
        source_paper=citing,
        target_paper=cited,
        relationship_type="SIMILAR_TO",
        origin_type="computed",
        score=2.75,
    )
    session.add_all([reference, similarity])
    session.flush()

    assert reference.citing_paper_id == citing.id
    assert reference.cited_paper_id == cited.id
    assert similarity.score == 2.75  # No scale/range is defined yet.

    session.add(
        PaperRelationship(
            source_paper=citing,
            target_paper=cited,
            relationship_type="CITES",
            origin_type="provider",
        )
    )
    with pytest.raises(IntegrityError):
        session.flush()
    session.rollback()


def test_reference_resolution_and_self_citation_constraints(session: Session) -> None:
    paper = add_paper(session, "Paper")
    source = MetadataSource(
        provider_name="fixture provider",
        retrieved_at=datetime.now(timezone.utc),
    )
    session.add(source)
    session.flush()

    session.add(
        PaperReference(
            citing_paper=paper,
            cited_paper=None,
            external_reference_key="unresolved-ref-1",
            resolution_status="unresolved",
            source_record=source,
        )
    )
    session.flush()

    session.add(
        PaperReference(
            citing_paper=paper,
            cited_paper=paper,
            external_reference_key="self-ref",
            resolution_status="resolved",
            source_record=source,
        )
    )
    with pytest.raises(IntegrityError):
        session.flush()
    session.rollback()


def test_metadata_snapshot_is_structured_json(session: Session) -> None:
    paper = add_paper(session, "Paper")
    source = MetadataSource(
        provider_name="fixture provider",
        retrieved_at=datetime.now(timezone.utc),
    )
    snapshot = PaperMetadataSnapshot(
        paper=paper,
        metadata_source=source,
        snapshot={"title": "Paper", "authors": ["Example"]},
        observed_at=datetime.now(timezone.utc),
    )
    session.add(snapshot)
    session.flush()

    assert session.get(PaperMetadataSnapshot, snapshot.id).snapshot["title"] == "Paper"


def test_workspace_links_collections_and_notes_require_same_workspace_membership(
    session: Session,
) -> None:
    workspace = add_workspace(session)
    paper = add_paper(session, "Saved paper")
    session.add(WorkspacePaper(workspace=workspace, paper=paper))
    collection = Collection(workspace=workspace, name="Reading list")
    session.add(collection)
    session.flush()

    session.add(CollectionPaper(collection=collection, workspace_paper=session.get(
        WorkspacePaper, (workspace.id, paper.id)
    )))
    session.add(Note(workspace=workspace, paper=paper, body="Private note"))
    session.add(ResearchQuestion(workspace=workspace, question_text="A question?"))
    session.flush()

    second_workspace = add_workspace(session)
    session.add(Note(workspace=second_workspace, paper=paper, body="Invalid cross-workspace note"))
    with pytest.raises(IntegrityError):
        session.flush()
    session.rollback()


def test_alembic_initial_migration_applies_to_isolated_sqlite_database(tmp_path) -> None:
    database_path = tmp_path / "migration-test.sqlite"
    engine = create_engine(f"sqlite:///{database_path}")
    with engine.connect() as connection:
        connection.exec_driver_sql("PRAGMA foreign_keys=ON")
        config = Config(str(BACKEND_ROOT / "alembic.ini"))
        config.attributes["connection"] = connection
        command.upgrade(config, "head")
        table_names = set(inspect(connection).get_table_names())

        assert compare_metadata(MigrationContext.configure(connection), Base.metadata) == []

        command.downgrade(config, "base")
        assert set(inspect(connection).get_table_names()) == {"alembic_version"}

        command.upgrade(config, "head")
        table_names = set(inspect(connection).get_table_names())

    assert "papers" in table_names
    assert "paper_references" in table_names
    assert "paper_relationships" in table_names
    assert "collections" in table_names
    assert "alembic_version" in table_names
    engine.dispose()


def test_alembic_initial_migration_renders_for_postgresql_offline() -> None:
    config = Config(str(BACKEND_ROOT / "alembic.ini"))
    config.attributes["database_url"] = (
        "postgresql+psycopg://placeholder:placeholder@localhost/research_x"
    )
    output = __import__("io").StringIO()
    config.output_buffer = output

    command.upgrade(config, "head", sql=True)
    sql = output.getvalue()

    assert "CREATE TABLE papers" in sql
    assert "JSONB" in sql
