from .example import main
from .click_example import my_cmd


def test_example():
    """Test that the main example script always runs."""
    main()


def test_click_example():
    """Test that the click example script always runs."""
    try:
        my_cmd(("foo", "bar"))
    except SystemExit as exc:
        if exc.code != 0:
            raise exc
