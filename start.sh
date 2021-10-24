source activate qbot
cd ~/QQBOT
kill -s 9 `ps -aux | grep 'go-cqhttp' | awk '{print $2}'`
nohup ./go-cqhttp faststart > log 2>&1 &

cd ~/pyqbot/chizi_bot
python bot.py
