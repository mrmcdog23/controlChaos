@echo off
setlocal

:: ============================================================
::  Python 3.11 Silent Installer
::  Target directory: C:\Python\python311\
:: ============================================================

set PYTHON_VERSION=3.11.9
set INSTALL_DIR=C:\Python\python311
set INSTALLER_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-amd64.exe
set INSTALLER_FILE=%TEMP%\python-%PYTHON_VERSION%-amd64.exe
set PIPELINE_ROOT=%USERPROFILE%\Documents\Code\controlChaos

echo ============================================================
echo  Python %PYTHON_VERSION% Installer
echo  Target: %INSTALL_DIR%
echo ============================================================
echo.

:: Check if the install directory already exists
if exist "%INSTALL_DIR%\" (
    echo [WARNING] The directory "%INSTALL_DIR%" already exists.
    echo           Python may already be installed at this location.
    echo.
    if exist "%INSTALL_DIR%\python.exe" (
        echo  Detected version:
        "%INSTALL_DIR%\python.exe" --version
        echo.
    )
    echo  Skipping installation.
    echo ============================================================
) else (
    :: Download the installer using PowerShell
    echo [1/3] Downloading Python %PYTHON_VERSION% installer...
    powershell -Command "Invoke-WebRequest -Uri '%INSTALLER_URL%' -OutFile '%INSTALLER_FILE%' -UseBasicParsing"
    if %errorlevel% neq 0 (
        echo [ERROR] Download failed. Check your internet connection and try again.
        pause
        exit /b 1
    )
    echo        Download complete.
    echo.

    :: Run the silent install
    echo [2/3] Installing Python to %INSTALL_DIR% ...
    "%INSTALLER_FILE%" /quiet InstallAllUsers=0 TargetDir="%INSTALL_DIR%" Include_launcher=1 PrependPath=1 Include_pip=1
    if %errorlevel% neq 0 (
        echo [ERROR] Installation failed. Exit code: %errorlevel%
        pause
        exit /b 1
    )
    echo        Installation complete.
    echo.

    :: Clean up the installer
    echo [3/3] Cleaning up temporary files...
    del /f /q "%INSTALLER_FILE%"
    echo        Done.
    echo.

    :: Verify install
    echo ============================================================
    echo  Verifying installation...
    "%INSTALL_DIR%\python.exe" --version
    if %errorlevel% neq 0 (
        echo [WARNING] Python installed but could not be verified at %INSTALL_DIR%\python.exe
    ) else (
        echo  pip version:
        "%INSTALL_DIR%\python.exe" -m pip --version
        echo.
        echo  SUCCESS! Python is installed at: %INSTALL_DIR%
    )
)

echo  Python installation complete.
echo ============================================================



:: ============================================================
::  Cloning the git repo in documents
:: ============================================================

echo Cloning controlChaos repository...
if exist "%PIPELINE_ROOT%" (
    echo Directory already exists: %PIPELINE_ROOT%
    echo Skipping clone.
) else (
    git clone https://github.com/mrmcdog23/controlChaos "%PIPELINE_ROOT%"
)

if %ERRORLEVEL% == 0 (
    echo.
    echo Successfully cloned to %PIPELINE_ROOT%
) else (
    echo.
    echo Clone failed. Make sure Git is installed and you have access to the repo.
)

:: ============================================================
:: CreateShortcut.bat
:: Creates a desktop shortcut to a file using its own icon
:: ============================================================

:: --- CONFIGURATION (edit these two lines) ---
set TARGET=%PIPELINE_ROOT%\bat\control_chaos_launcher.bat
set ICON=%PIPELINE_ROOT%\core\icons\launcher_ico.ico
set SHORTCUT_NAME=Control Chaos Launcher
:: ---------------------------------------------

set DESKTOP=%USERPROFILE%\Desktop
set SCRIPT="%TEMP%\CreateShortcut.vbs"
set SHORTCUT=%DESKTOP%\%SHORTCUT_NAME%.lnk


echo Set oWS = WScript.CreateObject("WScript.Shell") > %SCRIPT%
echo Set oLink = oWS.CreateShortcut("%SHORTCUT%") >> %SCRIPT%
echo oLink.TargetPath = "%TARGET%" >> %SCRIPT%
echo oLink.IconLocation = "%ICON%, 0" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%

cscript /nologo %SCRIPT%
del %SCRIPT%

echo.
echo Done! Shortcut created on your Desktop: %SHORTCUT_NAME%.lnk


:: ============================================================
::  Run the virtual environment
:: ============================================================

echo Installing virtual environment...
echo %PIPELINE_ROOT%\bat\environment.bat

call %PIPELINE_ROOT%\bat\environment.bat
echo Installation complete!

pause
endlocal