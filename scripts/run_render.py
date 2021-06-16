#!/usr/bin/env python3
import argparse

from img2vid.slides import Project
from img2vid.configs import AppConfig
from img2vid.renderer import VideoRenderer


parser = argparse.ArgumentParser(description='Render video')
parser.add_argument(
    'source', type=str,
    help='full path of source json file, url supported')
parser.add_argument(
    'dest', type=str,
    help='full path of destination video file')

args = parser.parse_args()

filepath = args.source
dest_filepath = args.dest

project = Project()
project.load_from(filepath)

app_config = AppConfig()
app_config.set_scale(.25)

video_renderer = VideoRenderer.create_from_project(
    project, app_config
)

video_renderer.make_video(
    dest_filepath,
    lambda progress: print('Progress: {:03d}%'.format(int(100*progress)), end='\r')
)
