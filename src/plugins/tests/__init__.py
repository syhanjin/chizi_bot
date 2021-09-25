
from nonebot import on_command
from nonebot.adapters.cqhttp.event import PrivateMessageEvent
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.typing import T_State
from nonebot.adapters.cqhttp.permission import PRIVATE
from nonebot.adapters.cqhttp.message import MessageSegment as ms

t1 = on_command(
    'test1', permission=PRIVATE, priority=1, block=False
)


@t1.handle()
async def _(bot: Bot, event: PrivateMessageEvent):
    await bot.send(event, ms.json({
        "app": "com.tencent.miniapp",
        "desc": "",
        "view": "notification",
        "ver": "0.0.0.1",
        "prompt": "欢迎入群",
        "meta": {
            "notification": {
                "appInfo": {
                    "appName": "欢迎您加入滑稽云-战地4模块",
                    "appType": 4,
                    "appid": 1109659848,
                    "iconUrl": "http:\/\/q2.qlogo.cn\/headimg_dl?dst_uin=2336213669&amp;spec=5"
                },
                "data": [
                    {
                        "title": "温馨提示",
                        "value": "新人进群务必查看群 置顶公告"
                    },
                    {
                        "title": "温馨提示",
                        "value": "注册邮箱请使用QQ邮箱"
                    },
                    {
                        "title": "恶臭提示",
                        "value": "本群目前没有BF4以外的服务器"
                    }
                ],
                "title": "",
                "button": [
                    {
                        "name": "访问博客注册地址注册账号",
                        "action": "http:\/\/bk.hjiyun.cn\/wp-login.php?action=register"
                    },
                    {
                        "name": "博客首页",
                        "action": "https:\/\/bk.hjiyun.cn\/"
                    },
                    {
                        "name": "按钮坏了链接在置顶 公告里有",
                        "action": "https:\/\/bk.hjiyun.cn\/"
                    }
                ],
                "emphasis_keyword": ""
            }
        }
    }))
