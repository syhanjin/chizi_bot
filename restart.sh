#!/bin/bash
source activate qbot
cd ~/pyqbot/chizi_bot

kill -s 9 `ps -aux | grep 'python bot.py' | awk '{print $2}'`

screen -x qbot
python bot.py