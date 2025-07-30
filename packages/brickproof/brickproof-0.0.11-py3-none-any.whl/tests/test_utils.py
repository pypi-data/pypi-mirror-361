from brickproof.utils import (
    write_profile,
    get_profile,
    read_toml,
    write_toml,
    validate_toml,
    insert_ignore_statement,
    insert_dependencies,
)
import os


def test_write_bprc():
    file_path = "./.test_bprc"
    profile = "default"
    token = "DUMMY"
    workspace = "https://XXX-XXX-XXX.cloud.databricks.com"
    write_profile(
        file_path=file_path, profile=profile, token=token, workspace=workspace
    )

    assert os.path.isfile(file_path)


def test_get_profile():
    file_path = "./.test_bprc"
    profile = "default"

    target = {
        "profile": profile,
        "workspace": "https://XXX-XXX-XXX.cloud.databricks.com",
        "token": "DUMMY",
    }

    real = get_profile(file_path=file_path, profile=profile)

    assert target == real


def test_write_toml():
    file_path = "./test_brickproof.toml"
    write_toml(file_path=file_path)

    toml_doc = read_toml(file_path=file_path)

    assert toml_doc["repo"]["name"] == "test"


def test_validate_toml():
    toml_doc = read_toml("./test_brickproof.toml")
    config = validate_toml(toml_doc)
    assert config.job.runner == "default"


def test_insert_ignore_statement():
    runner_str = (
        """retcode = pytest.main(["-p", "no:cacheprovider","--capture=sys"{ignore}])"""
    )
    ignore = ["./tests/test_dummy.py", "dummy/tests/test_dummy2.py"]
    repo_name = "dummy"
    real = insert_ignore_statement(runner_str, ignore, repo_name)

    target = """retcode = pytest.main(["-p", "no:cacheprovider","--capture=sys","--ignore=dummy/tests/test_dummy.py","--ignore=dummy/tests/test_dummy2.py"])"""
    assert real == target


def test_insert_dependencies():
    requirements = ["requests", "tomlkit"]
    runner_str = "{requirements}"
    real = insert_dependencies(runner_str, requirements)
    target = "!pip install pytest requests tomlkit"

    assert real == target


def test_cleanup():
    file_path = "./test_brickproof.toml"
    if os.path.isfile(file_path):
        os.remove(file_path)

    file_path = "./.test_bprc"
    if os.path.isfile(file_path):
        os.remove(file_path)

    assert True
