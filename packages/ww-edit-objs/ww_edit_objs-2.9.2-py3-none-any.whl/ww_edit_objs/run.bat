@echo off
setlocal EnableExtensions DisableDelayedExpansion
:: protect cwd
pushd

set myPoetry=C:\miatech\python3\Scripts\poetry.exe

:: script is at proj_root/
cd /d %~dp0
for %%I in (%cd%) do set myServName=%%~nxI
%myPoetry% run python src\%myServName%_cli.py %*
if NOT %errorlevel% == 0 (
	goto :fail
)
popd
goto :EOF

:fail
popd

