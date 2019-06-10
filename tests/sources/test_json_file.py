import json
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from conifer.sources.json_file import JSONFileLoader

import pytest


# matches TEST_SCHEMA from conftest
TEST_DATA = {
    "foo": "fffff",
    "bar": {"nested": "cccc", "more_nested": {"subkey": 22}},
    "arraything": [5, 6, 7, 8],
}


@pytest.fixture
def open_json_file():
    sio = StringIO()
    sio.write(json.dumps(TEST_DATA))
    sio.seek(0)
    yield sio
    sio.close()


def test_json_file(open_json_file):
    loader = JSONFileLoader(fp=open_json_file)
    assert loader._data == TEST_DATA
