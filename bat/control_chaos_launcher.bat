:: ============================================================
:: Launch the Control Chaos launcher
:: ============================================================

@echo off
setlocal

echo "   ____            _             _    ____ _                     "
echo "  / ___|___  _ __ | |_ _ __ ___ | |  / ___| |__   __ _  ___  ___ "
echo " | |   / _ \| '_ \| __| '__/ _ \| | | |   | '_ \ / _` |/ _ \/ __|"
echo " | |__| (_) | | | | |_| | | (_) | | | |___| | | | (_| | (_) \__ \"
echo "  \____\___/|_| |_|\__|_|  \___/|_|  \____|_| |_|\__,_|\___/|___/"
echo ""
echo Launching Control Chaos launcher...

set CURRENT_ROOT=%~dp0
set "PIPELINE_ROOT=%CURRENT_ROOT:~0,-5%"
for %%I in ("%PIPELINE_ROOT%") do set ROOT_DIR=%%~dpI
echo Pipeline root: %PIPELINE_ROOT%


set PYTHONPATH=%PYTHONPATH%;%ROOT_DIR%virtual_env\python311\Lib\site-packages
set PYTHONPATH=%PYTHONPATH%;%PIPELINE_ROOT%\core\python
set PYTHONPATH=%PYTHONPATH%;%PIPELINE_ROOT%\core\python\cccore\pyside

"C:/Python/python311/python.exe" %PIPELINE_ROOT%\standalone\python\launcher\control_chaos_launcher.py
pause
