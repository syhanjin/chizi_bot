
import datetime
from threading import Event
from handles import User
import json
import nonebot
from nonebot import on_notice
from nonebot.adapters.cqhttp.utils import escape
from nonebot.adapters.cqhttp import Bot, GroupIncreaseNoticeEvent
from nonebot.adapters.cqhttp.message import MessageSegment as ms
from nonebot.adapters.cqhttp.permission import GROUP
import pymongo


client = pymongo.MongoClient('127.0.0.1', 27017)
db = client['qbot']

increase = on_notice(priority=2, permission=GROUP, block=False)


@increase.handle()
async def _(bot: Bot, event: GroupIncreaseNoticeEvent):
    data = db.increase.find_one({'group_id': event.group_id})
    if data == None:
        msg = '欢迎新成员，请先看群公告~~~'
    else:
        msg = data['msg']
    await nonebot.get_bot().send(event, f"[CQ:at,qq={event.user_id}]{msg}")
    return
