import requests
import json
import sys
import os
import tarfile
import shutil
from MotionPicture import *
import imp
import argparse
import getpass

parser = argparse.ArgumentParser(description="Render MotionPicture video segment from remote.")
parser.add_argument("--booking", nargs="?", default="-1", type=int,
                    help="Number of booking in one attempt")
parser.add_argument("--addr", required=True,
                    dest="base_url", help="URL of rendering server")
parser.add_argument("--user", required=True,
                    help="Username to login to server")
parser.add_argument("--project", required=True, help="Project name")
parser.add_argument("--workspace", required=True, help="Local directory to save project data")
parser.add_argument("--process", nargs="?", default=1, type=int,
                    help="Number of process to spawn")
args = parser.parse_args()

username = args.user
passwd = getpass.getpass("[{0}]'s password:".format(args.user))

base_url = args.base_url
project_name = args.project
workbase_path = args.workspace
process_count = args.process
booking_per_call = args.booking

def write_json_to_file(filepath, data):
    f = open(filepath, "w")
    json.dump(data, f)
    f.close()

def write_segment_status(segments_folder, segment):
    segment_folder = os.path.join(segments_folder, u"{0:04}".format(segment["id"]))
    if not os.path.exists(segment_folder):
        os.makedirs(segment_folder)
    status_file = os.path.join(segment_folder, "status.txt")
    write_json_to_file(status_file, active_segment)

mp_url = base_url + "/mp"
project_url = mp_url + "/project/" + project_name

s = requests.session()
login_data = {
    "username": username,
    "password": passwd
}
r=s.post(mp_url+'/login', login_data)
jr = json.loads(r.text)

if jr["result"] == "success":
    print("Fetching information about project [{0}]".format(project_name))
    r=s.get(project_url+'/info')
    project = json.loads(r.text)

    if project.get("id"):
        extras = project["extras"]

        local_project_path = os.path.join(workbase_path, u"{0}".format(project_name))
        if not os.path.exists(local_project_path):
            os.makedirs(local_project_path)

        local_data_path = os.path.join(local_project_path, project["data_file_name"])

        if not os.path.isfile(local_data_path):
            print("Downloading data-file of project [{0}]".format(project_name))
            f = open(local_data_path, "wb")
            r = s.get(project_url+"/data_file", stream=True)
            total_size = int(r.headers.get("Content-Length"))
            downloaded_size = 0
            for data in r.iter_content(chunk_size=4096):
                f.write(data)
                downloaded_size += len(data)
                percent = int(downloaded_size*100./total_size)
                sys.stdout.write("\rProgress: {0:>5}% (of {2:>10}/{1:<10} byte)".format(
                        percent, total_size, downloaded_size))
            f.close()
            print("\n")

        extracted_folder = local_data_path +  u"_extracted"
        if not os.path.exists(extracted_folder):
            os.makedirs(extracted_folder)

            print("Extracting data-file of project [{0}]".format(project_name))
            tar_ref = tarfile.open(local_data_path, "r")
            tar_ref.extractall(extracted_folder)


        segments_folder = os.path.join(local_project_path, u"segments")
        if not os.path.exists(segments_folder):
            os.makedirs(segments_folder)

        while True:
            active_segment = None
            for filename in sorted(os.listdir(segments_folder)):
                folder = os.path.join(segments_folder   , filename)
                if not os.path.isdir(folder):
                    continue
                status_file = os.path.join(folder, "status.txt")
                if not os.path.isfile(status_file):
                    seg = dict()
                else:
                    f = open(status_file, "r")
                    seg = json.load(f)
                    f.close()
                if seg.get("status") in ("Booked",):
                    active_segment = seg
                    break

            #Get new booking
            if not active_segment:
                bc = 0
                while bc<booking_per_call or booking_per_call<0:
                    print("Fetching next booking of project [{0}]".format(project_name))
                    r=s.get(project_url+'/book')
                    booking = json.loads(r.text)
                    if booking.get("id"):
                        booking["status"] = "Booked"
                        if not active_segment:
                            active_segment = booking
                        write_segment_status(segments_folder, booking)
                        print("Segment id {0} is booked.".format(booking["id"]))
                        bc += 1
                    else:
                        break
                    if booking_per_call<0:
                        break
                if bc == 0:
                    print("No booking can be made.")
                    break

            if active_segment:
                segment_folder = os.path.join(segments_folder, u"{0:04}".format(active_segment["id"]))
                if not os.path.exists(segment_folder):
                    os.makedirs(segment_folder)

                status_file = os.path.join(segment_folder, "status.txt")
                write_json_to_file(status_file, active_segment)

                temp_output_filename = os.path.join(
                    segment_folder, "temp_video{0}".format(extras["file_ext"]))

                output_filename = os.path.join(
                    segment_folder, "video{0}".format(extras["file_ext"]))

                #Make the movie
                if not os.path.isfile(output_filename):
                    pre_script = extras.get("pre_script")
                    if pre_script:
                        pre_script_path = os.path.join(extracted_folder, pre_script)
                        if os.path.isfile(pre_script_path):
                            imp.load_source("pre_script", pre_script_path)
                    print("Building segment id-{2}:{0}-{1}".format(
                        active_segment["start_time"], active_segment["end_time"], active_segment["id"]))

                    doc_filename = os.path.join(extracted_folder, project["main_filename"])

                    kwargs = dict(
                        src_filename = doc_filename,
                        dest_filename = temp_output_filename,
                        time_line = project["time_line_name"],
                        start_time = active_segment["start_time"],
                        end_time = active_segment["end_time"],
                        resolution = extras.get("resolution", "1280x720"),
                        process_count=process_count
                    )
                    extra_param_names = ["ffmpeg_params", "bit_rate", "codec", "fps"]
                    for param_name in extra_param_names:
                        if param_name in extras:
                            kwargs[param_name] = extras[param_name]

                    ThreeDShape.HQRender = True

                    doc_movie = DocMovie(**kwargs)
                    doc_movie.make()

                if os.path.isfile(temp_output_filename):
                    shutil.move(temp_output_filename, output_filename)

                if os.path.isfile(output_filename):
                    segment_url = project_url+"/segment/{0}".format(active_segment["id"])

                #Upload
                print("Uploading segment id-{2}:{0}-{1}".format(
                        active_segment["start_time"], active_segment["end_time"], active_segment["id"]))
                video_file = open(output_filename, "rb")
                r=s.post(segment_url+"/upload", files={"video": video_file})
                response = json.loads(r.text)

                if response.get("result") == "success":
                    active_segment["status"] = "Uploaded"
                    write_json_to_file(status_file, active_segment)
                    print("Segment id-{2}:{0}-{1} is uploaded.".format(
                        active_segment["start_time"], active_segment["end_time"], active_segment["id"]))
                active_segment = None
        #end while
    else:
        print("No project with name [{0}] is found.".format(project_name))
