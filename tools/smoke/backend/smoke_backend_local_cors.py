from __future__ import annotations

import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[3]
BACKEND = (ROOT / "backend").resolve()
backend_path = str(BACKEND)
sys.path[:] = [item for item in sys.path if str(Path(item or ".").resolve()) != backend_path]
sys.path.insert(0, backend_path)

os.environ["API_PREFIX"] = "/api/v1"


def _install_db_import_stubs() -> None:
    import sqlalchemy.ext.asyncio as sa_async

    def create_async_engine_stub(*args, **kwargs):  # type: ignore[no-untyped-def]
        class DummyEngine:
            pass

        return DummyEngine()

    class DummySessionMaker:
        def __init__(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            pass

        def __call__(self):  # type: ignore[no-untyped-def]
            class DummySessionContext:
                async def __aenter__(self):  # type: ignore[no-untyped-def]
                    return None

                async def __aexit__(self, *args):  # type: ignore[no-untyped-def]
                    return None

            return DummySessionContext()

    sa_async.create_async_engine = create_async_engine_stub
    sa_async.async_sessionmaker = DummySessionMaker


_install_db_import_stubs()

from app.core.config import LOCAL_DEV_CORS_ORIGINS, Settings  # noqa: E402
from app.main import app  # noqa: E402


def test_local_settings_keep_vite_origin_when_env_is_old() -> None:
    settings = Settings(
        _env_file=None,
        CORS_ORIGINS="http://localhost:5500,http://127.0.0.1:5500",
    )

    assert "http://127.0.0.1:5173" in settings.cors_origins
    assert "http://localhost:5173" in settings.cors_origins
    assert len(settings.cors_origins) == len(set(settings.cors_origins))


def test_production_settings_do_not_append_local_dev_origins() -> None:
    settings = Settings(
        _env_file=None,
        environment="production",
        debug=False,
        CORS_ORIGINS="https://example.com",
    )

    assert settings.cors_origins == ["https://example.com"]
    for origin in LOCAL_DEV_CORS_ORIGINS:
        assert origin not in settings.cors_origins


def test_app_returns_cors_header_for_vite_dev_server() -> None:
    client = TestClient(app)
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://127.0.0.1:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"


def main() -> None:
    test_local_settings_keep_vite_origin_when_env_is_old()
    test_production_settings_do_not_append_local_dev_origins()
    test_app_returns_cors_header_for_vite_dev_server()
    print("[smoke_backend_local_cors] passed")


if __name__ == "__main__":
    main()
