from conifer import Conifer


schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',  # meta-schema for this object
    'title': 'My apps configuration schema',
    'description': ('This is a Draft 04 JSON schema document describing valid configuration'
                    ' options for this application.'),
    'type': 'object',
    'properites': {
        'LOGGING': {
            'description': 'Options pertaining to logging for myapp',
            'type': 'object',
            'properties': {
                'VERBOSITY': {
                    'description': 'Logging verbosity for myapp',
                    'type': 'string',
                    'enum': ['DEBUG', 'INFO', 'WARN', 'ERROR'],
                    'default': 'INFO'
                },
                'OUTPUT_FILE': {
                    'description': '(optional) Absolute or relative file path for logging',
                    'type': ['string', 'null']
                },
            },
        },
        'DEBUG_MODE': {
            'description': 'Enable debug mode for my Flask app',
            'type': 'boolean',
            'default': False
        },
        'PORT': {
            'description': 'Port the application will listen on',
            'type': 'integer',
            'minimum': 1,
            'maximum': 65534,
            'default': 8080
        }
    }
}

derivations = {
    'DEBUG_PORT': {
        'description': 'Port the application will use for serving debug requests',
        'derivation': lambda myapp_port: myapp_port + 1,
        'parameters': ['PORT'],
    }
}

conf = Conifer(
    schema,
    derivations=derivations,
)


def main():
    assert conf['DEBUG_MODE'] is False
    assert conf['PORT'] == 8080
    assert conf['LOGGING']['VERBOSITY'] == 'INFO'
    assert conf['DEBUG_PORT'] == conf['PORT'] + 1


if __name__ == '__main__':
    main()
