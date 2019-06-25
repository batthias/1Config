"""Read a oneconfig file."""

import yaml
import sys

config_filename = sys.argv[0]
f = open(config_filename, 'r')
