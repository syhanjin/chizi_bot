import datetime
from handles import User
import random
import string
import pymongo
import pandas as pd

from src.plugins.messages import kws
from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp.message import MessageSegment as ms
from nonebot.adapters.cqhttp.permission import PRIVATE
from nonebot.adapters.cqhttp.event import PrivateMessageEvent

client = pymongo.MongoClient('127.0.0.1', 27017)
db = client['qbot']
userdb = client['user']


pri_group_kw = on_command(
    'kw', aliases={'修改群关键字', '编辑群关键字', '群关键字'},
    permission=PRIVATE
)

pri_group_kw_refresh = on_command(
    'kwrefresh', aliases={'刷新关键字缓存', 'rekw', '关键字刷新'},
    permission=PRIVATE
)


@pri_group_kw.handle()
async def _pgk_first(bot: Bot, event: PrivateMessageEvent, state: T_State):
    # 处理用户输入参数
    raw_args = str(event.get_message()).strip()
    if raw_args:
        arg_list = raw_args.split()
        # 将参数存入state以阻止后续再向用户询问参数
        state["group_id"] = arg_list[0]


# region 关键字编辑端
@pri_group_kw.got('group_id', prompt='群号？')
async def _pgk_last(bot: Bot, event: PrivateMessageEvent, state: T_State):
    # 在这里对参数进行验证
    try:
        group_id = int(state["group_id"])
    except:
        await pri_group_kw.reject("群号输入不正确")
    member = await bot.call_api('get_group_member_info', group_id=group_id, user_id=event.user_id)
    user = User(str(group_id), str(event.user_id))
    user.update_from_info(member)
    if not user.update_from_info(member) or user.admin == 0:
        await pri_group_kw.finish("你并非此群管理员")
    key = ''.join(random.sample((string.ascii_letters+string.digits)*64, 64))
    deadtime = datetime.datetime.now() + datetime.timedelta(hours=24)
    db.kw_edit.insert_one({
        'group_id': group_id,
        'key': key,
        'deadtime': deadtime
    })
    await pri_group_kw.finish(
        f"""编辑链接已生成
https://sakuyark.com/qbot/kw/{group_id}?key={key}
有效期至 {deadtime.__format__("%Y-%m-%d %H:%M:%S")}
修改完成后请发送指令 【刷新关键字缓存】 进行刷新
"""
    )
# endregion


@pri_group_kw_refresh.handle()
async def _pgk_refresh(bot: Bot, event: PrivateMessageEvent):
    # 载入缓存
    kws = pd.DataFrame(list(db.kw.find()))
    kws = kws[kws['opened']].groupby(['group_id', 'degree'])
    await bot.send(event,
                   f'''---缓存已刷新---
{kws.count()['id']}
''')


