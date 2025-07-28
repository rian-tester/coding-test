@echo off
echo InterOpera Docker Commands
echo ========================

:menu
echo.
echo 1. Build and start all services
echo 2. Stop all services
echo 3. Restart all services
echo 4. View logs
echo 5. Clean up (remove containers and images)
echo 6. Exit
echo.
set /p choice="Choose an option (1-6): "

if "%choice%"=="1" goto build_start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto restart
if "%choice%"=="4" goto logs
if "%choice%"=="5" goto cleanup
if "%choice%"=="6" goto exit
echo Invalid choice. Please try again.
goto menu

:build_start
echo Building and starting all services...
docker-compose up --build -d
echo Services are running!
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8000
echo Nginx: http://localhost:80
goto menu

:stop
echo Stopping all services...
docker-compose down
echo Services stopped.
goto menu

:restart
echo Restarting all services...
docker-compose restart
echo Services restarted.
goto menu

:logs
echo Showing logs (Press Ctrl+C to exit)...
docker-compose logs -f
goto menu

:cleanup
echo WARNING: This will remove all containers and images for this project.
set /p confirm="Are you sure? (y/N): "
if /i "%confirm%"=="y" (
    echo Cleaning up...
    docker-compose down -v --rmi all
    echo Cleanup complete.
) else (
    echo Cleanup cancelled.
)
goto menu

:exit
echo Goodbye!
pause
