SET CURRENT_ROOT=%~dp0
SET "PIPELINE_ROOT=%CURRENT_ROOT:~0,-5%"
FOR %%I IN ("%PIPELINE_ROOT%") DO SET ROOT_DIR=%%~dpI

set PYTHONPATH=%PYTHONPATH%;%ROOT_DIR%virtual_env\python311\Lib\site-packages
set PYTHONPATH=%PYTHONPATH%;%PIPELINE_ROOT%\core\python
set PYTHONPATH=%PYTHONPATH%;%PIPELINE_ROOT%\core\python\cccore\pyside

"C:/Python/python311/python.exe" %PIPELINE_ROOT%\standalone\python\slate_maker\slate_maker_ui.py
pause
