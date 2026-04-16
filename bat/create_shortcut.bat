
:: ============================================================
:: CreateShortcut.bat
:: Creates a desktop shortcut to a file using its own icon
:: ============================================================
set PIPELINE_ROOT=%USERPROFILE%\Documents\Code\controlChaos

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
