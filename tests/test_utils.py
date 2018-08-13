from conifer.utils import recursive_update

import pytest


@pytest.mark.parametrize('original, updates, expected', [
    ({}, {1: 2}, {1: 2}),
    ({'foo': 'bar'}, {'foo': 'baz'}, {'foo': 'baz'}),
    ({1: {2: 3}}, {1: {2: 4, 3: 5}}, {1: {2: 4, 3: 5}}),
])
def test_recursive_update(original, updates, expected):
    recursive_update(original, updates)
    assert original == expected
