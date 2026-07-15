#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import stat
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools/render_production_compose_config.py"


def load_tool():
    tools_path = str(ROOT / "tools")
    if tools_path not in sys.path:
        sys.path.insert(0, tools_path)
    spec = importlib.util.spec_from_file_location("v312_compose_render", TOOL)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load v312 Compose render tool")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    module = load_tool()
    readiness = module.inspect_config_render_readiness(ROOT, docker_executable="/fake/docker")
    assert readiness["result"] == module.READY_RESULT
    assert readiness["dockerCliAvailable"] is True
    assert readiness["realEnvironmentRead"] is False
    assert readiness["realSecretRead"] is False
    assert readiness["containerMutationApproved"] is False

    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        args_log = temp / "args.txt"
        fake_docker = temp / "docker"
        rendered = """name: rpg-prod-config-review-v312
services:
  backend:
    deploy:
      replicas: 1
    environment:
      DATABASE_URL: postgresql+asyncpg://review_user:review_password@managed-db.review.invalid:5432/rpg_game?sslmode=verify-full&sslrootcert=/run/secrets/postgres_ca.pem
      DEBUG: \"false\"
      ENVIRONMENT: production
    image: review.invalid/upgrade-rpg-backend@sha256:0000000000000000000000000000000000000000000000000000000000000000
    networks:
      edge: null
    read_only: true
    security_opt:
      - no-new-privileges:true
    secrets:
      - source: postgres_ca
        target: /run/secrets/postgres_ca.pem
networks:
  edge:
    name: rpg-prod-review-edge-v312
    external: true
secrets:
  postgres_ca:
    file: /temporary/review-only-postgres-ca.pem
"""
        fake_docker.write_text(
            "#!/usr/bin/env python3\n"
            "import pathlib, sys\n"
            f"pathlib.Path({str(args_log)!r}).write_text('\\n'.join(sys.argv[1:]), encoding='utf-8')\n"
            f"sys.stdout.write({rendered!r})\n",
            encoding="utf-8",
        )
        fake_docker.chmod(fake_docker.stat().st_mode | stat.S_IXUSR)
        result = module.execute_config_render(ROOT, docker_executable=str(fake_docker))
        assert result["result"] == module.EXECUTED_RESULT
        assert result["dockerSubcommand"] == "compose config"
        assert result["reviewSentinelsOnly"] is True
        assert result["rawRenderPersisted"] is False
        assert result["temporaryReviewFilesRemoved"] is True
        assert result["imagePullBuildExecuted"] is False
        assert result["containerCreateStartStopRemoveExecuted"] is False
        assert result["networkVolumeMutationExecuted"] is False
        assert result["databaseConnectionMutationExecuted"] is False
        assert result["alembicCommandExecuted"] is False
        state = result["renderedState"]
        assert state["services"] == ["backend"]
        assert state["hostPortsAbsent"] is True
        assert state["buildAbsent"] is True
        assert state["namedVolumesAbsent"] is True
        assert state["backendReplicas"] == 1

        args = args_log.read_text(encoding="utf-8").splitlines()
        assert args[0] == "compose"
        assert args[-1] == "config"
        assert not any(value in args for value in ("pull", "build", "up", "down", "run", "start", "stop", "rm"))
        env_index = args.index("--env-file") + 1
        assert not Path(args[env_index]).exists(), "temporary review env was not removed"

    print("OK: v312 production Compose config render-only smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
