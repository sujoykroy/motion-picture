import subprocess
from MotionPicture import DocMovie, ThreeDShape
from moviepy.editor import VideoFileClip, AudioFileClip
import argparse

def str2bool(value):
    if value.lower() in ("true", "yes"):
        return True
    return False

parser = argparse.ArgumentParser(description="Export MotionPicture video.")
parser.add_argument("--output", dest="dest_filename", required=True)
parser.add_argument("--hq_3d", help="High quality 3d rendering", default=True, type=str2bool)
parser.add_argument("--audio", nargs="?", default=True, type=str2bool)
parser.add_argument("--audio-only", nargs="?", default=False, type=str2bool,
                            help="Export only audio")
parser.add_argument("--time-line", nargs="?")
parser.add_argument("--camera", nargs="?")
parser.add_argument("--speed", nargs="?", default=1, type=float)
parser.add_argument("--bg-color", nargs="?")
parser.add_argument("--start-time", nargs="?", type=float, default=0)
parser.add_argument("--end-time", nargs="?", type=float)
parser.add_argument("--resolution", nargs="?", default="1920x1080")
parser.add_argument("--fps", nargs="?", default=25, type=int)
parser.add_argument("--ffmpeg-params", nargs="?")
parser.add_argument("--bit-rate", nargs="?", type=str)
parser.add_argument("--codec", nargs="?")
parser.add_argument("--dry", nargs="?", default=False, help="Do not render the final video.")
parser.add_argument("src_filename")
parser.add_argument("--process-count", nargs="?", default=1, type=int)
parser.add_argument("--gif-params", nargs="?", default="", type=str)
args = parser.parse_args()

ThreeDShape.HQRender = args.hq_3d#should be true in production mode

if args.codec == "mjpeg":
    if not args.ffmpeg_params:
        args.ffmpeg_params = "-q:v 2"

kwargs = dict(
    src_filename = args.src_filename,
    dest_filename = args.dest_filename,
    time_line = args.time_line,
    start_time = args.start_time,
    end_time = args.end_time,
    camera = args.camera,
    audio_only = args.audio_only,
    audio = args.audio,
    speed = args.speed,
    bg_color = args.bg_color,
    fps = args.fps,
    resolution = args.resolution,
    process_count=args.process_count,
    dry = args.dry,
    gif_params = args.gif_params
)
for param in ["ffmpeg_params", "bit_rate", "codec"]:
    value = getattr(args, param)
    if value:
        kwargs[param] = value

doc_movie = DocMovie(**kwargs)
doc_movie.make()

if not doc_movie.is_png and not doc_movie.is_gif:
    if args.audio_only:
        clip=AudioFileClip(args.dest_filename)
    else:
        clip=VideoFileClip(args.dest_filename)
    print(doc_movie.dest_filename, "duration is", clip.duration)
    subprocess.call(["vlc", doc_movie.dest_filename])
else:
    subprocess.call(["eog", doc_movie.dest_filename])
