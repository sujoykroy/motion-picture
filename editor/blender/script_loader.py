import argparse
import sys
import imp
import bpy

start_index = -1
for i in range(len(sys.argv)):
    if sys.argv[i] == "--":
        start_index = i+1
        break

comand_parser = argparse.ArgumentParser()
comand_parser.add_argument("--params_filepath")
command_args = comand_parser.parse_args(sys.argv[start_index:start_index+2])

blender_params = imp.load_source("blender_params", command_args.params_filepath)
arg_types = {"number":float, "int": int}
for key, item in blender_params.params_info.items():
    comand_parser.add_argument(
        "--{0}".format(key),
        type=arg_types.get(item["type"], str),
        default=item["default"])
comand_parser.add_argument("--designer_filepath")
comand_parser.add_argument("--image_filepath")
comand_parser.add_argument("--utils_folderpath")
comand_parser.add_argument("--progress", type=float)
command_args = comand_parser.parse_args(sys.argv[start_index:])

if command_args.utils_folderpath not in sys.path:
    sys.path.append(command_args.utils_folderpath)

designer_module = imp.load_source("designer_module", command_args.designer_filepath)
designer = designer_module.Designer()
designer.build(params=command_args)

bpy.context.scene.render.filepath = command_args.image_filepath
bpy.ops.render.render(write_still=True)
