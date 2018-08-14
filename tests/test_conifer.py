from conifer import Conifer

import pytest


TEST_SCHEMA = {
    'definitions': {
        'reftype': {
            'type': 'object',
            'properties': {
                'some_prop': {
                    'type': 'array',
                    'default': [1],
                },
            },
        },
    },
    'properties': {
        'foo': {
            'type': 'string',
            'default': 'bar',
            'randomextrakey': 'whocareslol',
        },
        'bar': {
            'type': 'object',
            'default': {},
            'properties': {
                'nested': {
                    'type': 'string',
                    'default': 'baz'
                },
                'more_nested': {
                    'type': 'object',
                    'default': {},
                    'properties': {
                        'subkey': {
                            'type': 'integer',
                            'default': 1
                        },
                    },
                },
            },
        },
        'array_thing': {'$ref': '#definitions/reftype'},
    },
}


@pytest.fixture()
def conf():
    return Conifer(TEST_SCHEMA)


def test_basic_default(conf):
    assert conf['foo'] == 'bar'


def test_nested_default(conf):
    assert conf['bar']['nested'] == 'baz'


def test_more_nested_default(conf):
    assert conf['bar']['more_nested']['subkey'] == 1


def test_ref_array_default(conf):
    assert conf['array_thing']['some_prop'] == [1]


@pytest.fixture(scope='function')
def conf_env_patch(monkeypatch):
    monkeypatch.setenv('foo', 'asdf')
    monkeypatch.setenv('bar_nested', 'asdf')
    monkeypatch.setenv('bar_more_nested_subkey', 2)
    return Conifer(TEST_SCHEMA)


def test_basic_env(conf_env_patch):
    assert conf_env_patch['foo'] == 'asdf'


def test_nested_env(conf_env_patch):
    assert conf_env_patch['bar']['nested'] == 'asdf'


def test_more_nested_env(conf_env_patch):
    assert conf_env_patch['bar']['more_nested']['subkey'] == 2
