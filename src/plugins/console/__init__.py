import asyncio
import nonebot
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp.event import PrivateMessageEvent
from nonebot.adapters.cqhttp.permission import PRIVATE
from nonebot.permission import SUPERUSER
from nonebot.plugin import load_plugins, on_command


reload = on_command(
    '重载插件', aliases={'插件重载'},
    priority=2, block=True, permission=SUPERUSER | PRIVATE
)


@reload.handle()
async def _(bot: Bot, event: PrivateMessageEvent):
    load_plugins('src/plugins')
    await bot.send(event, '重载成功')