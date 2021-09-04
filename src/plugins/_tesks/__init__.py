import re
import nonebot
from datetime import date
from nonebot import get_bot, scheduler
from apscheduler.triggers.date import DateTrigger

import pymongo

client = pymongo.MongoClient('127.0.0.1', 27017)
db = client['qbot']


@scheduler.scheduled_job("cron", date='*', hour='12', id="group_cards")
async def task_group_cards():
    groups = list(db.cards.find({'enable': True}))
    for i in groups:
        tmp = await nonebot.get_bot().call_api(
            'get_group_member_list',
            group_id = int(i['group_id'])
        )
        rec = re.compile(i['reg'])
        wrongs = []
        if tmp.get('data'):
            for u in tmp.get('data'):
                card = u.get('card') or u.get('nickname')
                if not rec.search(card):
                    wrongs.append(u['group_id'])
                    

    return