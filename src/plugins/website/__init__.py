import nonebot
import asyncio
import subprocess
from nonebot.permission import SUPERUSER
from nonebot.adapters.cqhttp.permission import PRIVATE
from nonebot.plugin import on_command
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp.event import PrivateMessageEvent

__usage__ = '<SUPERUSER> 控制网站'
__help__version__ = '0.1.1'
__help__plugin_name__ = '网站控制bot段'


restart = on_command(
    'website restart', aliases={'网站重启', '重启网站'},
    priority=2, block=True, permission=SUPERUSER | PRIVATE
)
update = on_command(
    'website_update', aliases={'网站更新', '更新网站'},
    priority=2, block=True, permission=SUPERUSER | PRIVATE
)


@restart.handle()
async def _(bot: Bot, event: PrivateMessageEvent):
    subp = subprocess.Popen(
        '/root/restart_website.sh', encoding="utf-8", shell=True
    )
    while True:
        if subp.poll() is not None and subp.poll() == 0:
            await bot.send(event, f'''重启成功！''')
            return
        await asyncio.sleep(1)


@update.handle()
async def _(bot: Bot, event: PrivateMessageEvent):
    subp = subprocess.Popen(
        '/root/website/gitpull.sh', encoding="utf-8", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    while True:
        if subp.poll() is not None and subp.poll() == 0:
            await bot.send(
                event,
                f'''{subp.communicate()[0]}
{subp.communicate()[1]}'''
            )
            return
        await asyncio.sleep(1)
