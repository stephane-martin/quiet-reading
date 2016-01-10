# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
from os.path import join, abspath, dirname

from quiet.main import main

if __name__ == '__main__':
    this_dir = abspath(dirname(__file__))
    os.environ['QUIET_READING_CONFIG_PATH'] = join(this_dir, 'configdev.toml')
    main()
