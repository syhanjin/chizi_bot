import json
import re
import pymongo

from nonebot import on_command
from nonebot.adapters.cqhttp import Bot, MessageEvent
from nonebot.adapters.cqhttp.message import MessageSegment as ms
from nonebot.adapters.cqhttp.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER
from nonebot.typing import T_State

set_ban = on_command(
    "禁言", priority=2, permission=GROUP_ADMIN | GROUP_OWNER | SUPERUSER
)
cancel_ban = on_command(
    "解禁", aliases={'解除禁言'}, priority=2, permission=GROUP_ADMIN | GROUP_OWNER | SUPERUSER
)


@set_ban.handle()
async def handle_first_receive(bot: Bot, event: MessageEvent, state: T_State):
    args = str(event.get_message()).strip()
    r = re.compile("\[CQ:at,qq=(\d+)\] *(\d+)?")
    if not r.match(args):
        await bot.send(event, ms.text('格式错误, 标准格式：禁言 <@某人> [<禁言时间(s)>]'))
    qq = r.match(args).group(1)
    duration = r.match(args).group(2)
    if not duration:
        duration = 60
    if qq == 'all':
        await bot.call_api('set_group_whole_ban', {
            'group_id': json.loads(event.json())['group_id'],
            'enable': (not(duration == 0))
        })
        return
    await bot.call_api('set_group_ban', {
        'user_id': int(qq),
        'group_id': json.loads(event.json())['group_id'],
        'duration': duration
    })
    await bot.send(event, ms.text(qq))
@cancel_ban.handle()
async def handle_first_receive(bot: Bot, event: MessageEvent, state: T_State):
    args = str(event.get_message()).strip()
    r = re.compile("\[CQ:at,qq=(\d+)\]")
    if not r.match(args):
        await bot.send(event, ms.text('格式错误, 标准格式：解禁 <@某人>'))
    qq = r.match(args).group(1)
    if qq == 'all':
        await bot.call_api('set_group_whole_ban', {
            'group_id': json.loads(event.json())['group_id'],
            'enable': False
        })
        return
    await bot.call_api('set_group_ban', {
        'user_id': int(qq),
        'group_id': json.loads(event.json())['group_id'],
        'duration': 0
    })