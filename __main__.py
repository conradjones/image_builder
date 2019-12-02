#!/usr/bin/env python
# coding: utf8

import sys
from argparse import ArgumentParser
from parser import config

OPT_CONFIG = {
    'dest': 'config',
    'help': 'Config file',
    'required': True
}


def entrypoint():
    parser = ArgumentParser("imagebuilder")
    parser.add_argument("-c", "--config", **OPT_CONFIG)
    arguments = parser.parse_args(sys.argv[1:])

    config.parse_config(arguments.config)

if __name__ == '__main__':
    entrypoint()
