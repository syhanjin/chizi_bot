
import datetime
from handles.message_builder import welcome
from handles.group import User
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
    if data is None:
        msg = welcome(
            '欢迎上船',
            'https://sakuyark.com/static/images/icon.jpg',
            [('请先查看置顶公告',)]
        )
    else:
        if not data.get('opened'):
            return
        msg = data['msg']
    await bot.send(event, msg, at_sender=True)
    return


disban = on_notice(priority=1, block=False)


@disban.handle()
async def _disban(bot: Bot, event: GroupBanNoticeEvent):

    # await bot.send(event, ms.text('禁言事件测试：Event => ')+ms.text(str(event.json)))
    if event.user_id == 2819469337 and event.sub_type == 'ban':
        await bot.call_api(
            'set_group_ban',
            group_id=event.group_id,
            user_id=event.user_id,
            duration=0
        )
        await bot.send(event, ms.text('超级用户自动反禁言'))
