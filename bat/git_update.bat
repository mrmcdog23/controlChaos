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

