@echo off
REM Automatic brain plan to knowledge base plan synchronization script
REM This script should be scheduled to run regularly using Windows Task Scheduler

echo Starting plan synchronization at %date% %time%

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

REM Run the synchronization script
python scripts\sync_brain_plan.py >> logs\sync_plan.log 2>&1

REM Check if sync was successful
if %ERRORLEVEL% EQU 0 (
    echo Synchronization completed successfully at %date% %time% >> logs\sync_plan.log
    
    REM Check if git is available
    where git >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        REM Commit and push changes if any
        git add plan.md
        git diff --staged --quiet || (
            git commit -m "Auto-sync brain plan with knowledge base plan (%date%)"
            git push
            echo Changes committed and pushed to repository at %date% %time% >> logs\sync_plan.log
        )
    ) else (
        echo Git not found, changes not committed >> logs\sync_plan.log
    )
) else (
    echo Synchronization failed at %date% %time% >> logs\sync_plan.log
)

echo Plan synchronization completed at %date% %time%

REM Deactivate virtual environment if it was activated
if exist venv\Scripts\activate.bat (
    call venv\Scripts\deactivate.bat
)
