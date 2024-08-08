PowerWatch.sh                                                                               
#!/bin/bash

source /home/powermeter/fs_powerwatch_sw/env/bin/activate
exec python /home/powermeter/fs_powerwatch_sw/fs_powerwatch_GUI.py
pause
