@echo off
setlocal

:: ---------------------------------------------------------------
:: Vibrante-Node  —  Build script for Python 3.10
:: Run from the node_based_app directory:
::   cd node_based_app
::   build_py310.bat
:: ---------------------------------------------------------------

set PY310=C:\Python310\python310.exe
set SPEC=vibrante_node.spec

:: Verify Python 3.10 is present
if not exist "%PY310%" (
    echo ERROR: Python 3.10 not found at %PY310%
    exit /b 1
)

echo Using: %PY310%
%PY310% --version

:: Clean previous build artefacts
echo.
echo Cleaning previous build...
if exist build rmdir /s /q build
if exist dist  rmdir /s /q dist

:: Run PyInstaller through the Python 3.10 interpreter so the
:: bundled runtime matches exactly.
echo.
echo Running PyInstaller...
%PY310% -m PyInstaller %SPEC% --noconfirm

if %ERRORLEVEL% neq 0 (
    echo.
    echo BUILD FAILED  (exit code %ERRORLEVEL%)
    exit /b %ERRORLEVEL%
)

echo.
echo BUILD SUCCEEDED
echo Output: dist\Vibrante-Node\Vibrante-Node.exe
endlocal
