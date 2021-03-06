
import datetime
from utils.message_builder import welcome_card
from utils.group import User
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

welcome = on_notice(priority=2, block=False)


@welcome.handle()
async def _(bot: Bot, event: GroupIncreaseNoticeEvent):
    data = db.welcome.find_one({'group_id': event.group_id})
    at_sender = False
    if data is None:
        msg = welcome_card(
            '欢迎上船',
            f'http://p.qlogo.cn/gh/{event.group_id}/{event.group_id}/0',
            [('请先查看置顶公告',)]
        )
    else:
        if not data.get('opened'):
            return
        type = data.get('type')
        if type == 'text':
            msg = data['text']
            at_sender = True
        elif type == 'card':
            msg = welcome_card(
                data['text'],
                data.get('icon') or f'http://p.qlogo.cn/gh/{event.group_id}/{event.group_id}/0',
                data.get('tips'),
                data.get('buttons')
            )
        else :
            return
    await bot.send(event, msg, at_sender=at_sender)
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
