@echo off
setlocal

echo ========================================
echo   Git Rollback and Pull
echo ========================================
echo.


:: Prompt for git directory
cd /d "%USERPROFILE%\Documents\Code\controlChaos"

:: Check if we're in a git repo
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
    echo ERROR: Not inside a Git repository.
    pause
    exit /b 1
)

:: Show current branch and any local changes
echo Current branch:
git branch --show-current
echo.
echo Local changes:
git status --short
echo.

:: Fetch remote changes without applying them
echo Checking remote for updates...
git fetch
if errorlevel 1 (
    echo ERROR: Git fetch failed.
    pause
    exit /b 1
)

:: Compare local HEAD to remote tracking branch
for /f %%i in ('git rev-parse HEAD') do set LOCAL=%%i
for /f %%i in ('git rev-parse @{u}') do set REMOTE=%%i

if "%LOCAL%"=="%REMOTE%" (
    echo.
    echo Already up to date. No reset or pull needed.
    echo ========================================
    pause
    exit /b 0
)

:: Reset local changes
echo.
echo [1/2] Resetting local changes...
git reset --hard HEAD
if errorlevel 1 (
    echo ERROR: Git reset failed.
    pause
    exit /b 1
)

:: Remove untracked files and directories
git clean -fd
if errorlevel 1 (
    echo ERROR: Git clean failed.
    pause
    exit /b 1
)
echo Local changes cleared.

:: Perform git pull
echo.
echo [2/2] Pulling latest from remote...
git pull
if errorlevel 1 (
    echo ERROR: Git pull failed.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Done! Reset and pull complete.
echo ========================================
pause
