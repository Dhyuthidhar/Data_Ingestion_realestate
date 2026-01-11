@echo off
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat
echo ✅ Virtual environment activated
python --version
pip --version
echo.
echo 💡 To deactivate: type 'deactivate'
