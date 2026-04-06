echo "Installing python 3.12 site-packages..."

SET CURRENT_ROOT=%~dp0
SET "PIPELINE_ROOT=%CURRENT_ROOT:~0,-5%"
FOR %%I IN ("%PIPELINE_ROOT%") DO SET ROOT_DIR=%%~dpI
SET SITE_PACKAGES_311=%ROOT_DIR%virtual_env\python311
SET SITE_PACKAGES_311_NOPYSIDE=%ROOT_DIR%virtual_env\python311_nopyside

py -3.11 -m venv %SITE_PACKAGES_311%
"C:/Python/python311/python.exe" -m pip install -r "%PIPELINE_ROOT%/requirements/requirements311.txt" --target %SITE_PACKAGES_311%\Lib\site-packages

py -3.11 -m venv %SITE_PACKAGES_311_NOPYSIDE%
"C:/Python/python311/python.exe" -m pip install -r "%PIPELINE_ROOT%/requirements/requirements311_nopyside.txt" --target %SITE_PACKAGES_311_NOPYSIDE%\Lib\site-packages

pause
