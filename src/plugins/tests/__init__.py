
from nonebot import on_command
from nonebot.adapters.cqhttp.event import PrivateMessageEvent
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.typing import T_State
from nonebot.adapters.cqhttp.permission import PRIVATE
from nonebot.adapters.cqhttp.message import MessageSegment as ms
from handles.message_builder import welcome

t1 = on_command(
    'test1', permission=PRIVATE, priority=1, block=False
)


@t1.handle()
async def _(bot: Bot, event: PrivateMessageEvent):
    await bot.send(event, welcome(
        '欢迎',
        'https://sakuyark/static/images/icon.png',
        [{'title':'温馨提示','value':'我就是测试'}],
        [{'name':'Sakuyark','action':'https://sakuyark'}]
        ))
