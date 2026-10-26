@echo off
setlocal

cd /d "%~dp0"

if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
)

if exist "docs" rmdir /s /q "docs"

set "PYTHONPATH=%CD%\src;%PYTHONPATH%"

powershell -NoProfile -ExecutionPolicy Bypass -Command "$src=(Resolve-Path '.\src').Path; $mods=Get-ChildItem $src -Recurse -File -Filter '*.py' | Where-Object { $_.Name -ne '__init__.py' -and $_.FullName -ne (Join-Path $src 'main.py') -and $_.FullName -notmatch '[\\/](build|dist|__pycache__)[\\/]' } | ForEach-Object { $m=$_.FullName.Substring($src.Length+1); $m=$m -replace '\.py$',''; $m -replace '[\\/]', '.' }; if (-not $mods) { Write-Error 'No Python modules found'; exit 1 }; python -m pdoc -o '.\docs' $mods; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }"

if errorlevel 1 (
    echo Documentation generation failed.
    pause
    exit /b 1
)

python "%~dp0generate_folder_view.py" --src "%~dp0src" --docs "%~dp0docs"

echo Documentation generated in .\docs
pause