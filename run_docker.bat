@echo off

REM Check if the container already exists and remove it if it does
docker ps -a | findstr mathgenius_container > nul
if %errorlevel% equ 0 (
    echo Removing existing container...
    docker rm -f mathgenius_container
)

REM Build the Docker image
echo Building Docker image...
docker build -t mathgenius .

REM Run the Docker container
echo Running Docker container...
docker run -d -p 5000:5000 -v %cd%:/app -v %cd%/app/static:/app/app/static -e FLASK_ENV=development -e FLASK_DEBUG=1 --name mathgenius_container mathgenius

echo Docker container is now running.