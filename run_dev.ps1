# run_dev.ps1

# Check if the .venv directory exists
if (-not (Test-Path .\.venv -PathType Container)) {
    Write-Host "Virtual environment not found. Creating one..."
    # Ensure Python is accessible, might need to use 'python' or 'py' depending on setup
    python -m venv .venv 
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create virtual environment. Make sure Python is installed and in your PATH."
        exit 1
    }
    Write-Host "Virtual environment created."
} else {
    Write-Host "Virtual environment found."
}

# Activate the virtual environment
Write-Host "Activating virtual environment..."
# Note: Execution policy might prevent this. User might need to run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process 
# before running this script for the first time.
try {
    . .\.venv\Scripts\Activate.ps1
    Write-Host "Virtual environment activated."
} catch {
    Write-Error "Failed to activate virtual environment. Execution Policy might be restricted." 
    Write-Error "Try running 'Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process' in your PowerShell terminal and then run this script again."
    exit 1
}

# Install/update requirements
Write-Host "Installing/updating requirements from requirements.txt..."
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install requirements."
    exit 1
}
Write-Host "Requirements installed."

# Run the Uvicorn server
Write-Host "Starting the Uvicorn development server..."
# Use the command found in app/main.py
# Note: Using 'python -m uvicorn' can sometimes be more reliable than calling 'uvicorn' directly
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dirs app

Write-Host "Server stopped."

# Optional: Deactivate environment if script finishes (though server usually runs until stopped)
# Deactivate-Venv # This command might not be available by default, activation handles path changes. 