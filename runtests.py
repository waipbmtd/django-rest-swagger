#!/usr/bin/env python
import os
import sys
if '--lintonly' in sys.argv:
    import subprocess
    FLAKE8_ARGS = ['rest_framework_swagger', 'tests', '--ignore=E501', 'docs']
    def exit_on_failure(ret, message=None):
        if ret:
            sys.exit(ret)
    def flake8_main(args):
        print('Running flake8 code linting')
        ret = subprocess.call(['flake8'] + args)
        print('flake8 failed' if ret else 'flake8 passed')
        return ret
    exit_on_failure(flake8_main(FLAKE8_ARGS))
else:
    from django.core.management import execute_from_command_line

    sys.path.append("./example")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example.settings")
    import django.conf as conf
    execute_from_command_line([sys.argv[0], "test"])
