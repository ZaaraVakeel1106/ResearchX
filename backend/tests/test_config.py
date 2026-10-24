from app.core.config import Settings


def test_cors_origins_are_loaded_from_environment(monkeypatch) -> None:
    monkeypatch.setenv(
        "RESEARCH_X_CORS_ALLOWED_ORIGINS",
        " https://research.example/, http://localhost:5173 ",
    )
    config = Settings(_env_file=None)

    assert config.cors_origins == [
        "https://research.example",
        "http://localhost:5173",
    ]


def test_empty_cors_origin_configuration_disables_cross_origin_access() -> None:
    config = Settings(_env_file=None, cors_allowed_origins=" , ")

    assert config.cors_origins == []
