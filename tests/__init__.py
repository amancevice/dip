import dip.config

CONFIG = dip.config.DipConfig(**{
    'dips': {
        'fizz': {
            'branch': 'master',
            'env': {
                'FIZZ': 'BUZZ',
                'JAZZ': 'RAZZ'
            },
            'home': '/path/to/fizz',
            'path': '/path/to/bin',
            'remote': 'origin'
        },
        'buzz': {
            'branch': None,
            'env': {},
            'home': '/path/to/buzz',
            'path': '/path/to/bin',
            'remote': 'origin'
        },
        'jazz': {
            'branch': None,
            'env': {
                'FIZZ': 'BUZZ',
                'JAZZ': 'RAZZ'
            },
            'home': '/path/to/jazz',
            'path': '/path/to/bin',
            'remote': None
        }
    },
    'home': '/path/to/config.json',
    'path': '/path/to/bin',
    'version': dip.__version__
})
