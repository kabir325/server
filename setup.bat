@echo off
echo ========================================
echo Smart Load Balancer Server Setup
echo ========================================
echo.

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Generating gRPC files...
python generate_grpc_files.py

echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo To start the server:
echo   1. Run: python smart_load_balancer_server.py
echo   2. Or run: start_server.bat
echo.
pause
