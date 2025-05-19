setlocal

set VENV_DIR= .\backend\venv
set BASE_URL=https://huggingface.co/facebook/bart-large-cnn/resolve/main/
set DOWNLOAD_DIR=.\backend\ai\models\bart-large-cnn
set SUMMARY_FILES=config.json merges.txt model.safetensors tokenizer.json vocab.json

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

            echo Downloading summarization models

            :: Create download directory if it doesn't exist
            if not exist "%DOWNLOAD_DIR%" (
                mkdir "%DOWNLOAD_DIR%"
            )

            for %%F in (%SUMMARY_FILES%) do (
                echo Downloading %BASE_URL%%%F and saving to %DOWNLOAD_DIR%\%%F...
                curl -L -O "%DOWNLOAD_DIR%\%%F" "%BASE_URL%%%F"
                if %errorlevel% neq 0 (
                    echo Failed to download %%F
                ) else {
                    echo Succesfully downloaded %%F
                }
            )

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
