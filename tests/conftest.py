import pytest

from conifer import Conifer


TEST_SCHEMA = {
    '$schema': 'http://json-schema.org/draft-04/schema',
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
        'array_thing': {
            '$ref': '#/definitions/reftype',
            'default': {}
        },
    },
}


@pytest.fixture()
def test_schema():
    return TEST_SCHEMA


@pytest.fixture()
def conf():
    return Conifer(TEST_SCHEMA)


@pytest.fixture(scope='function')
def conf_env_patch(monkeypatch):
    monkeypatch.setenv('foo', 'asdf')
    monkeypatch.setenv('bar_nested', 'asdf')
    monkeypatch.setenv('bar_more_nested_subkey', '2')
    return Conifer(TEST_SCHEMA)
