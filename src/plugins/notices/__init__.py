
import datetime
from handles import User
import json
import nonebot
from nonebot import on_notice
from nonebot.permission import SUPERUSER
from nonebot.adapters.cqhttp import Bot, GroupIncreaseNoticeEvent, GroupBanNoticeEvent
from nonebot.adapters.cqhttp.message import MessageSegment as ms
from nonebot.adapters.cqhttp.permission import GROUP
import pymongo


client = pymongo.MongoClient('127.0.0.1', 27017)
db = client['qbot']

increase = on_notice(priority=2, block=False)


@increase.handle()
async def _increase(bot: Bot, event: GroupIncreaseNoticeEvent):
    data = db.increase.find_one({'group_id': event.group_id})
    if data == None:
        msg = '欢迎新成员，请先看群公告~~~'
    else:
        msg = data['msg']
    await bot.send(event, f"{msg}", at_sender=True)
    return


disban = on_notice(property=1, block=False, permission=GROUP)


@disban.handle()
async def _disban(bot: Bot, event: GroupBanNoticeEvent):

    await bot.send(event, ms.text('禁言事件测试：Event => ')+ms.text(str(event.json)))
    # if event.user_id != 'all'
    # await bot.call_api('set_group_ban')
