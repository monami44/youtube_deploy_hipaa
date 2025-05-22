#!/bin/bash
set -e

# Load environment variables from .env file if it exists
if [ -f .env ]; then
  echo "Loading environment variables from .env file"
  export $(grep -v '^#' .env | xargs)
fi

# Print Azure Storage environment variables for debugging
echo "Using Azure Storage settings:"
echo "AZURE_STORAGE_ACCOUNT_NAME: ${AZURE_STORAGE_ACCOUNT_NAME}"
echo "AZURE_STORAGE_CONTAINER_NAME: ${AZURE_STORAGE_CONTAINER_NAME}"
echo "POLL_INTERVAL_SECONDS: ${POLL_INTERVAL_SECONDS}"

# Start the API server in the background
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

# Start the worker in the background
python -m app.worker.main &
WORKER_PID=$!

# Handle termination signals
trap "kill $API_PID $WORKER_PID; exit" SIGINT SIGTERM

# Keep the script running
wait $API_PID $WORKER_PID 