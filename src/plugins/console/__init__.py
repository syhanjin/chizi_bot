import asyncio
import os
import subprocess
import nonebot
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp.event import PrivateMessageEvent
from nonebot.adapters.cqhttp.permission import PRIVATE
from nonebot.permission import SUPERUSER
from nonebot.plugin import load_plugins, on_command


restart = on_command(
    '重启', aliases={'bot重启'},
    priority=2, block=True, permission=SUPERUSER | PRIVATE
)


@restart.handle()
async def _(bot: Bot, event: PrivateMessageEvent):
    pid = os.getpid()
    subp = subprocess.Popen('./restart.sh', shell=True)
