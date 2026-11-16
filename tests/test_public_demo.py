import os
import tempfile
from pathlib import Path

from streamlit.testing.v1 import AppTest

from database import get_default_db_path


def test_public_demo_uses_system_temporary_database(monkeypatch):
    monkeypatch.delenv("LEARNING_AGENT_DB_PATH", raising=False)
    monkeypatch.setenv("PUBLIC_DEMO", "true")

    db_path = get_default_db_path().resolve()

    assert db_path.parent == Path(tempfile.gettempdir()).resolve()
    assert db_path.name == "learning_agent_public_demo.db"


def test_public_demo_warning_is_rendered_before_page_content(tmp_path, monkeypatch):
    monkeypatch.setenv("LEARNING_AGENT_DB_PATH", str(tmp_path / "app.db"))
    monkeypatch.setenv("PUBLIC_DEMO", "true")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    app_path = os.path.join(os.path.dirname(__file__), "..", "app.py")

    at = AppTest.from_file(app_path, default_timeout=20).run()
    warning_text = "请勿上传真实学生姓名、作答或照片"
    assert not at.exception
    assert any(warning_text in item.value for item in at.warning)
