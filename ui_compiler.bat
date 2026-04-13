@echo off
echo Compiling UI files...

for %%f in (*.ui) do (
    echo Processing %%f...
    pyside6-uic.exe %%f -o ui_%%~nf.py
)

echo Done