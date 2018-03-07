@ECHO OFF
REM This is sample script to build Windows executable of img2vid application

SET NUITKA_PATH=C:\Users\sujoykroy\Downloads\Nuitka-0.5.28.2\bin\nuitka
SET IMAGE_MAGICK_INSTALLER=C:\Users\sujoykroy\Downloads\ImageMagick-6.9.9-36-Q16-HDRI-x64-dll.exe
SET REPO_DIR=C:\Devel\img2vid
SET DIST_ROOT_DIR=C:\Users\sujoykroy\Img2VidBuild\

SET DIST_DIR=%DIST_ROOT_DIR%image2video.dist\
SET ZIP_DIST_FILE=%DIST_ROOT_DIR%image2video.zip


REM python "%NUITKA_PATH%" --recurse-all "%REPO_DIR%\scripts\image2video.py" --output-dir="%DIST_ROOT_DIR%\" --standalone --show-modules --python-version=3.6  --python-flag=no_site --file-reference-choice=runtime

Pause

REM Copy Tk/Tcl files
xcopy C:\ActiveTcl\lib\tcl8.6 %DIST_DIR%ActiveTcl\lib\tcl8.6 /S /Y /I
xcopy C:\ActiveTcl\lib\tk8.6 %DIST_DIR%ActiveTcl\lib\tk8.6 /S /Y /I

del %ZIP_DIST_FILE%
"C:\Program Files\7-Zip\7z.exe" a  -r %ZIP_DIST_FILE%  %DIST_DIR% %IMAGE_MAGICK_INSTALLER%