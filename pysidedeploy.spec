[app]

# title of your application
title = BatteryParametrizator

# project root directory. default = The parent directory of input_file
project_dir = .

# source file entry point path. default = main.py
input_file = py\main.py

# directory where the executable output is generated
exec_directory = ./dist

# path to the project file relative to project_dir
project_file = 

# application icon
icon = C:\Users\admin\AppData\Local\Programs\Python\Python313\Lib\site-packages\PySide6\scripts\deploy_lib\pyside_icon.ico

[python]

# python path
python_path = C:\Users\admin\Desktop\parametrizator\venv\Scripts\python.exe

# python packages to install
packages = Nuitka==2.7.11

[qt]

# qt modules used. comma separated
modules = Core,Gui,Widgets

# qt plugins used by the application. only relevant for desktop deployment
# for qt plugins used in android application see [android][plugins]
plugins = generic,iconengines,imageformats,platforms,platformthemes,styles

[nuitka]

# mode of using nuitka. accepts standalone or onefile. default = onefile
mode = standalone

# specify any extra nuitka arguments
extra_args = --quiet --noinclude-qt-translations --windows-disable-console

