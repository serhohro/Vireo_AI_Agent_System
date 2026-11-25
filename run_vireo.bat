@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

set "PROJECT_DIR=%CD%\Vireo_AI_Agent_System"
if not exist "%PROJECT_DIR%\main.py" (
    if exist "%CD%\main.py" (
        set "PROJECT_DIR=%CD%"
    ) else (
        echo [ERROR] Cannot find main.py. Run setup_vireo_project.bat first.
        exit /b 1
    )
)

cd /d "%PROJECT_DIR%"

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python was not found in PATH. Install Python 3.10+ and try again.
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment in .venv...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        exit /b 1
    )
)

call ".venv\Scripts\activate.bat"

if exist "requirements.txt" (
    python -m pip install --upgrade pip --quiet
    python -m pip install -r requirements.txt --quiet
)

set "PYTHONPATH=%PROJECT_DIR%"
echo Running Vireo unit tests...
python -m pytest -q
if errorlevel 1 (
    echo [ERROR] Unit tests failed.
    exit /b 1
)

echo Running Vireo Autonomous Agent Network benchmark...
python main.py
if errorlevel 1 (
    echo [ERROR] Execution failed.
    exit /b 1
)

echo Done. Benchmark output saved to "%PROJECT_DIR%\results\latest_benchmark.json".
endlocal