#!/bin/sh

# If .env file exists, export its variables
if [ -f .env ]; then
  echo "Loading environment variables from .env"
  export $(cat .env | grep -v '^#' | xargs)
fi

# Start the Next.js application
exec npm run start 