@echo off
echo Syncing development dependencies...
uv sync --group dev
if %errorlevel% neq 0 (
    echo Error: uv sync failed.
    exit /b %errorlevel%
)

echo Building standalone executable with PyInstaller...
uv run pyinstaller --noconfirm spynetscan.spec
if %errorlevel% neq 0 (
    echo Error: PyInstaller build failed.
    exit /b %errorlevel%
)

echo Desktop build completed successfully!
pause
