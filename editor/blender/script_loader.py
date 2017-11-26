import argparse
import sys


comand_parser = argparse.ArgumentParser()
comand_parser.add_argument("--params_filepath")
comand_parser.add_argument("--designer_filepath")
comand_parser.add_argument("--image_filepath")

start_index = -1
for i in range(len(sys.argv)):
    if sys.argv[i] == "--":
        start_index = i+1
        break
command_args = comand_parser.parse_args(sys.argv[start_index:])

blender_params = imp.load_source("blender_params", command_args.blender_params_filepath)
print(blender_params)
arg_types = {"number":float, "int": int}
for key, item in blender_params.params_info.items():
    comand_parser.add_argument(
        "--{0}".format(key),
        type=arg_types.get(item["type"], str),
        default=item["default"])
command_args = comand_parser.parse_args(sys.argv[start_index:])

import imp
designer_module = imp.load_source("designer_module", command_args.designer_filepath)
designer = designer_module.Designer(params=command_args)

