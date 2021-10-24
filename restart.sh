#!/bin/bash
cd ~/pyqbot/chizi_bot

read pid
kill -9 $pid

python bot.py