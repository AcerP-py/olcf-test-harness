import pytest

from harness.config import Config

# ---------------------------------------------------------------------------
# Test Config
# ---------------------------------------------------------------------------


def test_config_instantiate(monkeypatch):
    c = Config()
    assert c._config == {}

    monkeypatch.setenv("OTH_TEST_VAR", "pytest")
    c = Config()
    assert c._config == {"test_var": "pytest"}


def test_config_set():
    c = Config()

    print("-------------")
    c.set("pytest:location", True)
    assert c._config["pytest"]["location"] == True

    print("-------------")
    # overwrite data
    with pytest.raises(KeyError):
        c.set("pytest:location:error", True)

    print("-------------")
    # invalid identifier
    with pytest.raises(ValueError):
        c.set("pytest:1error", True)


def test_config_get():
    c = Config()

    assert c.get("") == {}
    assert c.get("pytest:location") == None
    with pytest.raises(KeyError):
        assert c.get("pytest:location", none_on_miss=False) == None

    c._config["pytest"] = {}
    c._config["pytest"]["location"] = True
    assert c.get("") == {"pytest": {"location": True}}
    assert c.get("pytest:location") == True

    # invalid identifier
    with pytest.raises(ValueError):
        assert c.get("pytest:1error") == True
