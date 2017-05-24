"""
Terminal colors.
"""
import colored

AMBER = colored.fg('yellow')
BLUE = colored.fg('blue')
RED = colored.fg('red')
TEAL = colored.fg('spring_green_1')


def amber(text):
    """ Shortcut for colored.stylize(). """
    return colored.stylize(text, AMBER)


def blue(text):
    """ Shortcut for colored.stylize(). """
    return colored.stylize(text, BLUE)


def red(text):
    """ Shortcut for colored.stylize(). """
    return colored.stylize(text, RED)


def teal(text):
    """ Shortcut for colored.stylize(). """
    return colored.stylize(text, TEAL)
