@echo off
rem ------------------------------------------------------------------------------------------------
rem
rem Create a virtual environmen
rem
rem Autor: Heribert Füchtenhans
rem
rem ------------------------------------------------------------------------------------------------

if exist .\venv_windows rd /S /Q .\venv_windows

echo venv_windows wird erstellt
python -m venv venv_windows
if errorlevel 1 (
	echo venv_windows konnte nicht installiert werden.
	pause
	goto :Ende
)

echo Install requirements
call .\venv_windows\Scripts\Activate.bat
set AllwaysArgs=--trusted-host files.pythonhosted.org --trusted-host pypi.org --retries 1 --upgrade
python -m pip install %AllwaysArgs% --upgrade pip
python -m pip install %AllwaysArgs% -r requirements.txt
) else (
	call venv_windows\Scripts\activate.bat
)

pause Fertig...
