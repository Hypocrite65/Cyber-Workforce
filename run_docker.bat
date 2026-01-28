@echo off
set IMAGE_NAME=ai-collab-core

echo [Info] Checking Docker status...
docker info >nul 2>&1
if %errorlevel% neq 0 goto :ErrorDocker

REM 检查镜像是否存在
docker inspect %IMAGE_NAME% >nul 2>&1
if %errorlevel% equ 0 goto :Run

echo [Info] Image %IMAGE_NAME% not found. Building...
docker build -t %IMAGE_NAME% .

REM 构建后再次检查
docker inspect %IMAGE_NAME% >nul 2>&1
if %errorlevel% neq 0 goto :ErrorBuild

echo [Info] Build successful.

:Run
echo [Info] Running AI Collab...
echo [Info] Task: %*

docker run --rm -it ^
  -v "%cd%":/app ^
  %IMAGE_NAME% python -u main.py %*

if %errorlevel% neq 0 goto :ErrorExecution

echo [Success] Task completed.
goto :End

:ErrorDocker
echo [Error] Docker is NOT running or not installed.
echo Please start Docker Desktop and try again.
goto :End

:ErrorBuild
echo [Error] Docker build failed (Image build possibly failed).
goto :End

:ErrorExecution
echo [Error] Execution failed during docker run.
goto :End

:End
echo.
echo Press any key to exit...
pause >nul
