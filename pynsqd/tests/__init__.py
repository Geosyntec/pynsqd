from pkg_resources import resource_filename

import pynsqd


def test(*args):
    try:
        import pytest
    except ImportError as e:
        raise ImportError("`pytest` is required to run the test suite")

    options = [resource_filename('pynsqd', 'tests')]
    options.extend(list(args))
    return pytest.main(options)
