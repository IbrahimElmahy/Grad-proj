@echo off
setlocal enabledelayedexpansion

echo ==========================================================
echo           RVMS Project - Automated Startup Script
echo ==========================================================
echo.

:: Check for Python installation
echo Checking for Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your system PATH.
    echo Please install Python 3.10+ (specifically Python 3.11 recommended) and try again.
    pause
    exit /b 1
)
echo [OK] Python is installed.
echo.

:: Check for Node.js & npm
echo Checking for Node.js and npm...
node -v >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in your system PATH.
    echo Please install Node.js and npm and try again.
    pause
    exit /b 1
)
npm -v >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] npm is not installed or not in your system PATH.
    echo Please install Node.js and npm and try again.
    pause
    exit /b 1
)
echo [OK] Node.js and npm are installed.
echo.

:: Set up backend virtual environment
echo ==========================================================
echo Setting up Django Backend...
echo ==========================================================
cd backend

if not exist .venv (
    echo Creating virtual environment (.venv)...
    python -m venv .venv
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to create virtual environment.
        cd ..
        pause
        exit /b 1
    )
) else (
    echo Virtual environment (.venv) already exists.
)

echo Activating virtual environment...
call .venv\Scripts\activate

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing backend dependencies (this may take a few minutes for OpenCV/YOLO)...
pip install -r requirements.txt
if !errorlevel! neq 0 (
    echo [ERROR] Failed to install backend dependencies.
    cd ..
    pause
    exit /b 1
)

:: Copy openh264 DLL if present in backend directory to .venv Scripts
if exist openh264-1.8.0-win64.dll (
    echo Copying OpenH264 DLL to virtual environment...
    copy /y openh264-1.8.0-win64.dll .venv\Scripts\ >nul
)

echo Running database migrations...
python manage.py makemigrations
python manage.py migrate
if !errorlevel! neq 0 (
    echo [ERROR] Database migration failed.
    cd ..
    pause
    exit /b 1
)

echo Creating admin superuser if not exists...
python create_superuser.py

echo Creating demo safety officer and manager users...
python manage.py create_test_users

cd ..
echo [OK] Backend setup complete!
echo.

:: Set up frontend dependencies
echo ==========================================================
echo Setting up React Frontend...
echo ==========================================================
cd frontend

if not exist node_modules (
    echo Installing npm packages (this might take a while)...
    call npm install
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to install frontend npm packages.
        cd ..
        pause
        exit /b 1
    )
) else (
    echo Frontend dependencies are already installed.
)

cd ..
echo [OK] Frontend setup complete!
echo.

:: Start servers concurrently
echo ==========================================================
echo Starting Development Servers...
echo ==========================================================
echo.
echo [System Info]
echo - Frontend: http://localhost:5173
echo - Backend: http://localhost:8000
echo - Admin: User: admin / Pass: admin123
echo - Manager: User: manager / Pass: manager123
echo - Officer: User: officer / Pass: officer123
echo.
echo Launching backend and frontend in separate command windows...

:: Launch backend
start "RVMS Django Backend" cmd /k "cd backend && call .venv\Scripts\activate && python manage.py runserver 127.0.0.1:8000"

:: Launch frontend
start "RVMS Vite Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo All processes spawned. Enjoy!
echo.
pause
