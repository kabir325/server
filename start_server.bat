@echo off
echo ============================================================
echo   Smart AI Load Balancer v3.0 - Windows Startup
echo ============================================================
echo.
echo Starting the Smart Load Balancer services...
echo.
echo This will start:
echo   1. gRPC Server (port 50051)
echo   2. HTTP Wrapper (port 5001)
echo.
echo Press Ctrl+C to stop all services
echo ============================================================
echo.

python start_smart_loadbalancer.py

pause
