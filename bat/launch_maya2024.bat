@echo off
:: ============================================================
:: launch_maya2024.bat
:: Launches Autodesk Maya 2024 with the correct pipeline
:: environment variables configured.
:: ============================================================

:: --- Resolve directory paths ---
SET CURRENT_ROOT=%~dp0
SET "PIPELINE_ROOT=%CURRENT_ROOT:~0,-5%"
FOR %%I IN ("%PIPELINE_ROOT%") DO SET ROOT_DIR=%%~dpI

:: --- Python path configuration ---
set PYTHONPATH=C:\Program Files\Autodesk\Maya2024\Python\Lib\site-packages
set PYTHONPATH=%PYTHONPATH%;%ROOT_DIR%virtual_env\python311_nopyside\Lib\site-packages

:: --- Add control chaos pipeline ---
set PYTHONPATH=%PYTHONPATH%;%PIPELINE_ROOT%\core\python
set PYTHONPATH=%PYTHONPATH%;%PIPELINE_ROOT%\maya\python
set PYTHONPATH=%PYTHONPATH%;%PIPELINE_ROOT%\core\python\cccore\pyside

:: --- Maya environment paths ---
set MAYA_PLUG_IN_PATH=%PIPELINE_ROOT%\maya\plugins
set MAYA_SHELF_PATH=%PIPELINE_ROOT%\maya\shelves
set XBMLANGPATH=%PIPELINE_ROOT%\maya\shelves\icons

:: --- Debug output ---
echo "Python path: %PYTHONPATH%"

:: --- Launch Maya 2024 ---
"C:\Program Files\Autodesk\Maya2024\bin\maya.exe"
pause
