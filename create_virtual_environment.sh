#!/bin/bash

# ------------------------------------------------------------------------------------------------
#
# Create a virtual environment
#
# Autor: Heribert Füchtenhans
#
# ------------------------------------------------------------------------------------------------

if [ -d ./venv_linux ]; then
	rm --force --recursive -dir --interactive=never ./venv_linux
fi

echo "venv_linux wird erstellt"
python3 -m venv ./venv_linux

echo "Install requirements"
source ./venv_linux/bin/activate
AllwaysArgs='--trusted-host files.pythonhosted.org --trusted-host pypi.org --retries 1 --upgrade'
python3 -m pip --require-virtualenv install $AllwaysArgs --upgrade pip
pip3 --require-virtualenv install $AllwaysArgs -r requirements.txt
pip3 --require-virtualenv install $AllwaysArgs -r requirements_other.txt


read -p "Fertig ..."

