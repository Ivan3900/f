@echo off
REM ===========================================================================
REM  Build script for Phone Link Kiosk Launcher
REM  Run this ON YOUR WINDOWS PC from inside the phone_link_kiosk folder.
REM  Produces a single standalone .exe in the dist\ folder.
REM ===========================================================================

echo.
echo [1/3] Installing Python dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo.
echo [2/3] Building single-file executable with PyInstaller...
REM --onefile      : bundle everything into one .exe
REM --noconsole    : hide the console window (remove this to see live logs)
REM --name         : output exe name
REM --add-data     : ship config.py alongside (so you can tweak without rebuild)
pyinstaller --onefile --noconsole --name PhoneLinkKiosk ^
  --hidden-import win32timezone ^
  main.py
if errorlevel 1 goto :error

echo.
echo [3/3] Done!  Your executable is at:  dist\PhoneLinkKiosk.exe
echo Double-click it to run. Edit config.py and rebuild to change behaviour.
goto :eof

:error
echo.
echo BUILD FAILED. See the messages above.
exit /b 1
