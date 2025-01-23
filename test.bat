@echo off

set VENV_DIR=.venv
set PYTHON_FILE=rpa_CMC_solana.py

REM Step 1: Check if the virtual environment already exists
if not exist %VENV_DIR% (
    echo Virtual environment not found. Creating a new one...
    python -m venv %VENV_DIR%
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment.
        exit /b 1
    )
    echo Virtual environment created successfully.
) else (
    echo Virtual environment already exists.
)

REM Step 2: Activate the virtual environment
echo Activating virtual environment...
call %VENV_DIR%\Scripts\activate
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment.
    exit /b 1
)
echo Virtual environment activated.

REM Step 3: Install dependencies from requirements.txt if it exists
if exist requirements.txt (
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Failed to install dependencies.
        exit /b 1
    )
    echo Dependencies installed successfully.
) else (
    echo No requirements.txt file found. Skipping dependency installation.
)

REM Step 4: Run the Python script
if exist %PYTHON_FILE% (
    echo Running Python script: %PYTHON_FILE%...
    python %PYTHON_FILE%
    if %errorlevel% neq 0 (
        echo Python script execution failed.
        exit /b 1
    )
    echo Python script executed successfully.
) else (
    echo Python script "%PYTHON_FILE%" not found. Exiting.
    exit /b 1
)

REM End of script
echo All steps completed successfully.
