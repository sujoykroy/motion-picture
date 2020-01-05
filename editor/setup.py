from setuptools import setup
setup(
    name = 'MotionPicture',
    version = '0.3',
    package_dir = {'MotionPicture': 'MotionPicture'},
    packages = ['MotionPicture',
                'MotionPicture.commons',
                'MotionPicture.audio_tools',
                'MotionPicture.editors',
                'MotionPicture.gui_utils',
                'MotionPicture.settings',
                'MotionPicture.shape_creators',
                'MotionPicture.shapes',
                'MotionPicture.tasks',
                'MotionPicture.time_line_boxes',
                'MotionPicture.time_lines',
                'MotionPicture.shapes',
                'MotionPicture.extras'],
    package_data = {'MotionPicture': [
                'settings/main_style.css', 'settings/menu_accel_icon.txt',
                'icons/*.xml', 'icons/predrawns/*.xml']}
)
