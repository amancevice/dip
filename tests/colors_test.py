import mock
from dip import colors


@mock.patch('colored.stylize')
def test_amber(mock_style):
    """ Shortcut for colored.stylize(). """
    colors.amber('TEST')
    mock_style.assert_called_once_with('TEST', colors.AMBER)


@mock.patch('colored.stylize')
def test_blue(mock_style):
    """ Shortcut for colored.stylize(). """
    colors.blue('TEST')
    mock_style.assert_called_once_with('TEST', colors.BLUE)


@mock.patch('colored.stylize')
def test_red(mock_style):
    """ Shortcut for colored.stylize(). """
    colors.red('TEST')
    mock_style.assert_called_once_with('TEST', colors.RED)


@mock.patch('colored.stylize')
def test_teal(mock_style):
    """ Shortcut for colored.stylize(). """
    colors.teal('TEST')
    mock_style.assert_called_once_with('TEST', colors.TEAL)
