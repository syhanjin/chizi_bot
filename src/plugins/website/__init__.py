import nonebot
import asyncio
import subprocess
from nonebot.permission import SUPERUSER
from nonebot.adapters.cqhttp.permission import PRIVATE
from nonebot.plugin import on_command
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp.event import PrivateMessageEvent

restart = on_command(
    'website restart', aliases={'网站重启', '重启网站'},
    priority=2, block=True, permission=SUPERUSER | PRIVATE
)


@restart.handle()
async def _(bot: Bot, event: PrivateMessageEvent):
    subp = subprocess.Popen(
        '/root/restart_website.sh', stdout=subprocess.STDOUT, encoding="utf-8", shell=True
    )
    while True:
        if subp.poll() is not None and subp.poll() == 0:
            await bot.send(event, f'''重启成功，输出：\n{subp.communicate()}''')
            return
        await asyncio.sleep(1)
