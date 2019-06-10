"""Tests of basic Conifer class using a couple different fixtures.

See conftest.py for fixtures.
"""


def test_basic_default(conf):
    assert conf["foo"] == "bar"


def test_nested_default(conf):
    assert conf["bar"]["nested"] == "baz"


def test_more_nested_default(conf):
    assert conf["bar"]["more_nested"]["subkey"] == 1


def test_ref_array_default(conf):
    assert conf["array_thing"]["some_prop"] == [1]


def test_basic_env(conf_env_patch):
    assert conf_env_patch["foo"] == "asdf"


def test_nested_env(conf_env_patch):
    assert conf_env_patch["bar"]["nested"] == "asdf"


def test_more_nested_env(conf_env_patch):
    assert conf_env_patch["bar"]["more_nested"]["subkey"] == 2
