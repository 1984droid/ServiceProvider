Write-Host "Starting setup script test..."
& cmd /c "echo y | setup_from_repo.bat"
Write-Host "Script completed with exit code: $LASTEXITCODE"
