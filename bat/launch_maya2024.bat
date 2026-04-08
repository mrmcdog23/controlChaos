SET CURRENT_ROOT=%~dp0
SET "PIPELINE_ROOT=%CURRENT_ROOT:~0,-5%"
FOR %%I IN ("%PIPELINE_ROOT%") DO SET ROOT_DIR=%%~dpI
set PYTHONPATH=C:\Program Files\Autodesk\Maya2024\Python\Lib\site-packages
set PYTHONPATH=%PYTHONPATH%;%ROOT_DIR%virtual_env\python311_nopyside\Lib\site-packages
set PYTHONPATH=%PYTHONPATH%;%PIPELINE_ROOT%\core\python
set PYTHONPATH=%PYTHONPATH%;%PIPELINE_ROOT%\maya\python

set MAYA_PLUG_IN_PATH=%PIPELINE_ROOT%\maya\plugins
set MAYA_SHELF_PATH=%PIPELINE_ROOT%\maya\shelves
set XBMLANGPATH=%PIPELINE_ROOT%\maya\icons

echo "Python path: %PYTHONPATH%"

"C:\Program Files\Autodesk\Maya2024\bin\maya.exe"
pause
