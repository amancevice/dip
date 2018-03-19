from dip import settings


SETTINGS = {'fizz': {'name': 'fizz',
                     'home': '/path/to/fizz',
                     'path': '/path/to/bin',
                     'env': {'FIZZ': 'BUZZ', 'JAZZ': 'RAZZ'},
                     'git': {'branch': 'master',
                             'remote': 'origin',
                             'auto_upgrade': False}},
            'buzz': {'name': 'buzz',
                     'home': '/path/to/buzz',
                     'path': '/path/to/bin',
                     'git': {'remote': 'origin', 'auto_upgrade': False}},
            'jazz': {'name': 'jazz',
                     'home': '/path/to/jazz',
                     'path': '/path/to/bin',
                     'env': {'FIZZ': 'BUZZ', 'JAZZ': 'RAZZ'}}}


# pylint: disable=too-many-ancestors
class MockSettings(settings.Settings):
    def __init__(self):
        super(MockSettings, self).__init__(**SETTINGS)
        self.filepath = '/path/to/settings.json'
