#! /usr/bin/env python3

import sys
import os
from subprocess import run, Popen

SYS_PYTHON = "python"
ENV_PYTHON = "./.venv/bin/python"

if not os.path.exists("./.venv"):
    print("INFO: Creating venv")
    run([SYS_PYTHON, "-m", "venv", ".venv"])

freeze_proc = run([ENV_PYTHON, "-m", "pip", "freeze"], capture_output = True)
freeze_output = freeze_proc.stdout.decode()
req = open("./requirements.txt", "r+")

unsync = False
for line in zip(freeze_output.splitlines(), req.readlines()):
    if line[0].strip() != line[1].strip():
        unsync = True
        break

if unsync:
    print("INFO: Requirements not met. Syncing")
    run([ENV_PYTHON, "-m", "pip", "install", "-r", "requirements.txt"])
    req.seek(0)
    req.write(freeze_output)
    req.truncate()

req.close()

run([ENV_PYTHON, "./main.py"])
sys.exit(0)


# if [[ ! -d .venv ]]; then
#     if [[ -z $($SYS_PYTHON --version) ]]; then
# 	echo "ERROR: Please install python from your system repository."
#     fi
#
#     $SYS_PYTHON -m venv .venv
#     if [[ $? -ne 0 ]]; then
# 	echo "ERROR: Could not create virtual enviroment"
#     fi
#     echo "INFO: Created virtual enviroment"
#
#     $ENV_PYTHON -m pip install -r ./requirements.txt
#     if [[ $? -ne 0 ]]; then
# 	echo "ERROR: Could not install packages"
#     fi
#     echo "INFO: Packages installed into .venv"
# fi
#
# $ENV_PYTHON -m pip install -r ./requirements.txt
# $ENV_PYTHON main.py
