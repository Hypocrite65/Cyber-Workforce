#!/bin/bash
IMAGE_NAME="ai-collab-core"

# 1. Check Docker Daemon Status
if ! docker info > /dev/null 2>&1; then
    echo "❌ [Error] Docker is not running. Please start Docker Engine."
    exit 1
fi

# 2. Check and Build Image
if [[ "$(docker images -q $IMAGE_NAME 2> /dev/null)" == "" ]]; then
    echo "🏗️  [Info] Image $IMAGE_NAME not found. Building..."
    docker build -t $IMAGE_NAME .
    
    # Check build result
    if [ $? -ne 0 ]; then
        echo "❌ [Error] Build failed. Please check Dockerfile or network."
        exit 1
    fi
fi

# 3. Run Container
echo "🚀 [Info] Running Cyber-Workforce..."
echo "📋 [Task] $@"

# Note: On Windows Git Bash, paths might need care via MSYS_NO_PATHCONV, 
# but generally "$(pwd)" works fine for modern Docker settings.
docker run --rm -it \
  -v "$(pwd)":/app \
  $IMAGE_NAME python -u main.py "$@"

if [ $? -eq 0 ]; then
    echo "✅ [Success] Task completed."
else
    echo "❌ [Error] Execution failed."
fi
