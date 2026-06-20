#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "=========================================================="
echo "          RVMS Project - Automated Startup Script"
echo "=========================================================="
echo

# Check for Python 3
if ! command -v python3 &> /dev/null
then
    echo "[ERROR] python3 is not installed or not in your PATH."
    echo "Please install Python 3.10+ and try again."
    exit 1
fi
echo "[OK] Python 3 is installed."

# Check for Node.js
if ! command -v node &> /dev/null
then
    echo "[ERROR] Node.js is not installed or not in your PATH."
    exit 1
fi
echo "[OK] Node.js is installed."

# Check for npm
if ! command -v npm &> /dev/null
then
    echo "[ERROR] npm is not installed."
    exit 1
fi
echo "[OK] npm is installed."
echo

# 1. Setup Backend
echo "=========================================================="
echo "Setting up Django Backend..."
echo "=========================================================="
cd backend

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment (.venv)..."
    python3 -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Upgrading pip..."
python -m pip install --upgrade pip

echo "Installing backend dependencies (this may take a few minutes)..."
pip install -r requirements.txt

echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Creating admin superuser if not exists..."
python create_superuser.py

echo "Creating demo safety officer and manager users..."
python manage.py create_test_users

cd ..
echo "[OK] Backend setup complete!"
echo

# 2. Setup Frontend
echo "=========================================================="
echo "Setting up React Frontend..."
echo "=========================================================="
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing npm packages..."
    npm install
else
    echo "Frontend dependencies are already installed."
fi

cd ..
echo "[OK] Frontend setup complete!"
echo

# 3. Running Servers Concurrently
echo "=========================================================="
echo "Starting Development Servers..."
echo "=========================================================="
echo
echo "[System Info]"
echo " - Frontend: http://localhost:5173"
echo " - Backend: http://localhost:8000"
echo " - Admin: User: admin / Pass: admin123"
echo " - Manager: User: manager / Pass: manager123"
echo " - Officer: User: officer / Pass: officer123"
echo
echo "Press [Ctrl+C] to stop both servers."
echo

# Launch Django Backend in the background
cd backend
source .venv/bin/activate
python manage.py runserver 127.0.0.1:8000 &
BACKEND_PID=$!
cd ..

# Launch Vite Frontend in the background
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Handle Ctrl+C termination elegantly
cleanup() {
    echo
    echo "Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo "Clean shutdown completed."
    exit 0
}

trap cleanup INT TERM

# Keep the script alive
wait
