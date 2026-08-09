import inspect

import pytest

from scripts.seed_secrets import parse_env_file


@pytest.mark.unit
def test_seed_secrets_has_no_delete_calls():
    """Security DoD: Assert programmatically that seed_secrets contains no delete method references."""
    import scripts.seed_secrets as ss_mod

    func_source = inspect.getsource(ss_mod.seed_secrets)

    # Assert no delete_secret or force_delete calls exist in function implementation
    assert "delete_secret" not in func_source
    assert "force_delete" not in func_source
    assert "delete" not in func_source


@pytest.mark.unit
def test_parse_env_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=bar\n# Comment\nBAZ='qux'\nEMPTY=\n", encoding="utf-8")

    parsed = parse_env_file(env_file)
    assert parsed == {"FOO": "bar", "BAZ": "qux"}
