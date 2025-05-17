@echo off
setlocal

set VENV_DIR= .\backend\venv

where python >nul 2>nul
if %errorlevel%==0 (
    echo Python is installed.
    python --version

    where node >nul 2>nul
    if %errorlevel%==0 (
        echo Node is installed.
        node --version

        where npm >nul 2>nul
        if %errorlevel%==0 (
            if not exist %VENV_DIR% (
                echo Creating virtual environment in %VENV_DIR%...
                python -m venv %VENV_DIR%
            ) else (
                echo Virtual environment already exists in %VENV_DIR%
            )

            echo Activating virtual environment...
            call %VENV_DIR%\Scripts\activate.bat

            echo Installing Python packages...
            pip install -r .\backend\requirements.txt

            echo Initializing database...
            python .\backend\database\createTables.py

            echo Installing Node packages...
            pushd /frontend
            npm install 
            popd

            echo Starting services...
            call start.bat
        ) else (
            echo npm is NOT installed. Install npm and run setup again.
        )
        
    ) else (
        echo Node is NOT installed. Install Node and run setup again.
    )
) else (
    echo Python is NOT installed. Install Python and run setup again.
)
