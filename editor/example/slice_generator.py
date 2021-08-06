import subprocess
import argparse

def create_pose_slice(duration, start_pose, end_pose=None):
    if not end_pose:
        end_pose = start_pose
    return """
    <time_slice duration="{duration}" end_value="{end_value}" linked="False" start_value="{start_value}">
    <prop_data key="start_pose" type="str" value="{start_pose}"/>
    <prop_data key="end_pose" type="str" value="{end_pose}"/>
    <prop_data key="type" type="str" value="pose"/>
    </time_slice>
    """.format(
        duration=duration, end_value=1, start_value=0,
        start_pose=start_pose, end_pose=end_pose
    )

def create_prop_slice(duration, start_value, end_value=None):
    if end_value is None:
        end_value = start_value
    return """
    <time_slice duration="{duration}" end_value="{end_value}" linked="False" start_value="{start_value}">
    </time_slice>
    """.format(
        duration=duration, end_value=end_value, start_value=start_value
    )


def create_pose_time_slice(shape_name, poses_at_times, total_duration):
    poses_at_times_secs = {}
    for mark, pose in poses_at_times.items():
        mins, secs = mark.split(":")
        poses_at_times_secs[int(mins)*60+int(secs)] = pose
    poses_at_times = poses_at_times_secs

    marks = list(sorted(poses_at_times.keys()))
    prev_mark_at = 0
    pose_slices = []
    visible_slices = []
    marks.append(total_duration)
    for mark_i, mark_at in enumerate(marks[:-1]):
        if mark_i == 0 and mark_at:
            visible_slices.append(create_prop_slice(mark_at, 0))

        pose_duration = marks[mark_i+1] - mark_at
        pose_slices.append(create_pose_slice(
            pose_duration, poses_at_times[mark_at]))

        visible_duration = min(5, pose_duration)
        visible_slices.append(create_prop_slice(visible_duration, 1))
        hide_duration = pose_duration - visible_duration
        if hide_duration:
            visible_slices.append(create_prop_slice(hide_duration, 0))
        prev_mark_at = mark_at

    return """
    <shape_time_line shape_name="{shape_name}">
        <prop_time_line prop_name="internal">
        {pose_slices}
        </prop_time_line>
        <prop_time_line prop_name="visible">
        {visible_slices}
        </prop_time_line>
    </shape_time_line>""".format(
        shape_name=shape_name,
        pose_slices="\n".join(pose_slices),
        visible_slices="\n".join(visible_slices)
    )



parser = argparse.ArgumentParser(description="Generate Slice XML.")
parser.add_argument("--caption-times", required=True)
parser.add_argument("--duration", required=True, type=float)

args = parser.parse_args()
# print(args)
captions = {}
caption_i = 0
for time_pos in args.caption_times.split(","):
    time_pos = time_pos.strip()
    if not time_pos:
        continue

    caption_i += 1
    captions[time_pos] = "Pose_{:03d}".format(caption_i)

print(create_pose_time_slice(
    "captions", captions, args.duration
))
