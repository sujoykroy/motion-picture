#!/usr/bin/env python3
from img2vid.slides import Project
from img2vid.configs import AppConfig
from img2vid.renderer import VideoRenderer

filepath = '/home/sujoy/img2vid_test.json'
dest_filepath = '/home/sujoy/img2vid_test.mov'

project = Project()
project.load_from(filepath)

video_renderer = VideoRenderer.create_from_project(
    project, AppConfig()
)

video_renderer.make_video(dest_filepath)
