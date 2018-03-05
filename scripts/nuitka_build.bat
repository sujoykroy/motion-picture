python nuitka --recurse-all C:\Devel\img2vid\scripts\run_simple.py --standalone --show-modules --python-version=3.6  --python-flag=no_site 

SET DIST_DIR=C:\Users\sujoykroy\Downloads\Nuitka-0.5.28.2\bin\run_simple.dist\
xcopy C:\ActiveTcl\lib\tcl8.6 %DIST_DIR%ActiveTcl\lib\tcl8.6 /S /Y /I

xcopy C:\ActiveTcl\lib\tk8.6 %DIST_DIR%ActiveTcl\lib\tk8.6 /S /Y /I


SET MAGICK_NAME=ImageMagick-6.9.9-Q16-HDRI
SET IMAGE_MAGICK_LOCAL=C:\Program Files\%MAGICK_NAME%\

xcopy "%IMAGE_MAGICK_LOCAL%CORE_RL_magick_.dll" "%DIST_DIR%%MAGICK_NAME%\" /Y /S /I
xcopy "%IMAGE_MAGICK_LOCAL%CORE_RL_wand_.dll" "%DIST_DIR%%MAGICK_NAME%\" /Y /S /I
