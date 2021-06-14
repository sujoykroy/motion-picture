#!/usr/bin/env python3
import argparse

import img2vid


parser = argparse.ArgumentParser(description='Render video')
parser.add_argument(
    'source', type=str,
    help='full path of source json file, url supported')

args = parser.parse_args()

filepath = args.source

img2vid.main(filepath=filepath)
