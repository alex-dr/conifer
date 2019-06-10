from conifer.sources.schema_utils import iter_schema


def test_iter_schema(test_schema):
    expected = [
        (
            ["foo"],
            {"type": "string", "default": "bar", "randomextrakey": "whocareslol"},
        ),
        (["bar", "nested"], {"type": "string", "default": "baz"}),
        (["bar", "more_nested", "subkey"], {"type": "integer", "default": 1}),
        (["array_thing", "some_prop"], {"type": "array", "default": [1]}),
    ]
    assert sorted(iter_schema(test_schema)) == sorted(expected)
