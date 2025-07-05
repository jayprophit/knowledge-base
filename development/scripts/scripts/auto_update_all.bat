@echo off
REM Automatic document and knowledge base update script
REM This script automates README, changelog updates and plan synchronization

echo Starting knowledge base update process at %date% %time%

REM Change to the knowledge base directory
cd /d F:\github\knowledge-base

REM Create logs directory if it doesn't exist
if not exist logs mkdir logs

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found, using system Python
)

echo.
echo Step 1: Synchronizing brain plan with knowledge base plan...
python scripts\sync_brain_plan.py >> logs\auto_update.log 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Brain plan synchronization failed. Check logs\auto_update.log for details.
) else (
    echo Brain plan synchronized successfully.
)

echo.
echo Step 2: Updating README.md and changelog.md...
python scripts\auto_update_docs.py --commit >> logs\auto_update.log 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Documentation update failed. Check logs\auto_update.log for details.
) else (
    echo Documentation updated successfully.
)

echo.
echo Knowledge base update completed at %date% %time%
echo See logs\auto_update.log for more details.

REM Deactivate virtual environment if it was activated
if exist venv\Scripts\activate.bat (
    call venv\Scripts\deactivate.bat
)

pause
