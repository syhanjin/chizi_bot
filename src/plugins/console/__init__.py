import asyncio
import os
import subprocess
import nonebot
from nonebot import permission
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp.event import PrivateMessageEvent
from nonebot.adapters.cqhttp.permission import PRIVATE
from nonebot.permission import SUPERUSER
from nonebot.plugin import load_plugins, on_command
from nonebot.typing import T_State


restart = on_command(
    '重启', aliases={'bot重启'},
    priority=2, block=True, permission=SUPERUSER | PRIVATE
)
update = on_command(
    '更新', aliases={'获取更新'},
    priority=2, permission=SUPERUSER | PRIVATE, block=True
)


@restart.handle()
async def _(bot: Bot, event: PrivateMessageEvent):
    subp = subprocess.Popen('./restart.sh', shell=True)


@update.handle()
async def _(bot: Bot, event: PrivateMessageEvent, state: T_State):
    fetch = subprocess.Popen(
        'git fetch origin master',
        shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE
    )
    while fetch.poll() is None:
        await asyncio.sleep(1)
    log = subprocess.Popen(
        'git log -p master.. origin/master',
        shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE
    )
    while log.poll() is None:
        await asyncio.sleep(1)
    await bot.send(
        event,
        f'''$ git fetch origin master\n{
            fetch.communicate()[1]
        }\n$ git log -p master.. origin/master\n{
            log.communicate()[1]
        }'''
    )

@update.got('merge')
async def _(bot: Bot, event: PrivateMessageEvent, state: T_State):
    pass
