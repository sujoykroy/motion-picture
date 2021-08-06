import subprocess
import argparse

parser = argparse.ArgumentParser(description="Stabilize Video.")
parser.add_argument("src")
parser.add_argument("dest")

args = parser.parse_args()

command = [
    "ffmpeg",
    "-i",
    args.src,
    "-vf", "vidstabdetect",
    "-f", "null", "-"
]
subprocess.call(command)

command = [
    "ffmpeg",
    "-i",
    args.src,
    "-vf", "vidstabtransform",
    args.dest
]
subprocess.call(command)

