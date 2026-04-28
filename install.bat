@echo off
echo Installing Battery Parametrizator

echo [1/3] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not founded!
    echo.
    exit /b 1
)
echo Python founded!
echo.

python -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" || (
    echo ERROR: install Python 3.10 or later
    exit /b 1
)

echo [2/3] Installing dependencies...
echo.
python -m pip install --upgrade pip -q
pip install -r requirements.txt
echo OK!
echo.

echo [3/3] Compiling UI...
if exist "ui_compiler.bat" (
    call ui_compiler.bat
) else (
    echo ERROR: ui_compiler.bat not founded!
    exit /b 1
)
echo.
echo Completed!
echo Запустите setup.bat для запуска приложения
pause