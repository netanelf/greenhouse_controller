#!/bin/bash

echo "arg1: " $1
x-terminal-emulator -e sh run_web_linux.sh
sudo sh run_brain_linux.sh $1