"""The two compose files (decision E-32) must not drift apart; the stack .env must cover them."""

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BUILD = (REPO / "docker-compose.yml").read_text(encoding="utf-8")
RUNTIME = (REPO / "compose.dockge.yaml").read_text(encoding="utf-8")
ENV_EXAMPLE = (REPO / ".env.example").read_text(encoding="utf-8")


def test_both_files_use_the_same_local_image():
    assert re.findall(r"image: (\S+)", BUILD) == ["fever:local"]
    assert re.findall(r"image: (\S+)", RUNTIME) == ["fever:local"]


def test_only_the_build_file_builds():
    assert "build:" in BUILD
    assert "build:" not in RUNTIME
    assert "pull_policy: never" in RUNTIME


def test_runtime_file_guards_data_directory_user_and_health():
    assert "create_host_path: false" in RUNTIME
    assert 'user: "${FEVER_UID:?' in RUNTIME
    assert "from fever.worker import healthcheck" in RUNTIME
    assert "restart: unless-stopped" in RUNTIME


def test_web_service_publishes_the_port_and_checks_health():
    assert '"0.0.0.0:${FEVER_WEB_PORT:?' in RUNTIME
    assert "fever.web.app:server" in RUNTIME and '"--workers", "1"' in RUNTIME
    assert "http://127.0.0.1:8050/health" in RUNTIME
    assert "FRED_API_KEY" not in RUNTIME.split("  web:")[1]  # the web never needs the secret


def test_image_contains_the_assets():
    assert "COPY assets/ assets/" in (REPO / "Dockerfile").read_text(encoding="utf-8")


def test_every_variable_of_the_runtime_file_is_in_the_env_template():
    used = set(re.findall(r"\$\{([A-Z_]+)", RUNTIME))
    defined = set(re.findall(r"^([A-Z_]+)=", ENV_EXAMPLE, flags=re.MULTILINE))
    assert used <= defined, used - defined


def test_env_template_keeps_secrets_empty():
    assert re.search(r"^FRED_API_KEY=$", ENV_EXAMPLE, flags=re.MULTILINE)
