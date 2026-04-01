SET CURRENT_ROOT=%~dp0
echo %CURRENT_ROOT%
set "PARENT_DIR=%CURRENT_ROOT:~0,-5%"
echo %PARENT_DIR%
"C:/Python/python311/python.exe" %PARENT_DIR%\standalone\python\slate_maker\slate_maker_ui.py
pause
