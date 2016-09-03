from distutils.core import setup
setup(
    name = 'MotionPicture',
    version = '0.1',
    package_dir = {'MotionPicture': 'src'},
    packages = ['MotionPicture',
                'MotionPicture.commons',
                'MotionPicture.editors',
                'MotionPicture.gui_utils',
                'MotionPicture.settings',
                'MotionPicture.shape_creators',
                'MotionPicture.shapes',
                'MotionPicture.tasks',
                'MotionPicture.time_line_boxes',
                'MotionPicture.time_lines',
                'MotionPicture.shapes'],
    package_data = {'MotionPicture': [
                'settings/main_style.css', 'settings/menu_accel_icon.txt', 'icons/*.*']}
)
