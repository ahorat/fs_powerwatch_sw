#!/bin/bash

./init_rs232.sh
exec python FsPowerWatchGui.py
pause
