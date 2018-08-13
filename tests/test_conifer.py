from conifer import Conifer


TEST_SCHEMA = {
    'properties': {
        'foo': {
            'type': 'string',
            'default': 'bar'
        }
    }
}


def test_basic_default():
    conf = Conifer(TEST_SCHEMA)
    assert conf['foo'] == 'bar'
