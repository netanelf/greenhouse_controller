#!/bin/bash

echo "arg1: " $1
cd /home/pi/workspace/greenhouse_controller
lxterminal -e "sh run_web_linux.sh"
lxterminal -e "sudo sh run_brain_linux.sh"