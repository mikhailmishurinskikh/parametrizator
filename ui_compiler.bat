@echo off
echo Compiling UI files...

if not exist "ui_py" mkdir ui_py

if not exist "ui" (
    echo Error: Folder "ui" not found!
    pause
    exit /b 1
)

for %%f in (ui\*.ui) do (
    echo Processing %%f...
    pyside6-uic.exe %%f -o ui_py\ui_%%~nf.py
)

echo Done