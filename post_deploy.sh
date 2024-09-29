#!/bin/bash
echo "Starting post-deployment script..."

echo "Current working directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"
echo "Current user: $(whoami)"

echo "Running database initialization script..."
python -m app.initial_data

if [ $? -eq 0 ]; then
    echo "Database initialization completed successfully."
else
    echo "Error: Database initialization failed."
    exit 1
fi

echo "Post-deployment script completed."