#!/usr/bin/env python
import os
import sys
import subprocess

if '--lintonly' in sys.argv:
    args = ['rest_framework_swagger', 'example']
    pylint_cmd = ['pylint'] + args
    pep8_cmd = ['pep8'] + args

    exit = False
    if subprocess.call(pylint_cmd):
        print('pylint check failed.')
        exit = True

    if subprocess.call(pep8_cmd):
        print('pep8 check failed.')
        exit = True

    if exit:
        sys.exit()

else:
    from django.core.management import execute_from_command_line

    sys.path.append("./example")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example.settings")
    execute_from_command_line([sys.argv[0], "test"])
