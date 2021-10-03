
import os
from typing import Union
import nonebot
from nonebot.adapters.cqhttp.message import MessageSegment as ms

NAME = list(nonebot.get_driver().config.nickname)[0]

'''
 "大家好，我是丙实。金牛座男一枚~[CQ:xml,data=<?xml version='1.0' encoding='UTF-8' ?><msg serviceID="104" templateID="1" brief="大家好，我是丙实。金牛座男一枚~"><item layout="2"><picture cover="" /><title>新人入群</title></item><source /></msg>,resid=104]"
'''


def introduction(
    text: str
) -> ms:
    """
    说明：
        生成一张入群介绍格式的 MessageSegment.text + MessageSegment.xml 消息
    参数：
        :param *text: 介绍内容
    """
    return ms.text(text) + ms.xml(
        f"""<?xml version='1.0' encoding='UTF-8' ?><msg serviceID="104" templateID="1" brief="{text}"><item layout="2"><picture cover="" /><title>{NAME} 来到了这里</title></item><source /></msg>"""
    )


def welcome_card(
    text: str,
    icon: str = '',
    tips: 'list[tuple[str, str] | list[str, str]] | tuple[str, str] | str' = [],
    buttons: 'list[tuple[str, str] | list[str, str]] | tuple[str, str]' = []
) -> ms:
    '''
    说明：
        生成一张欢迎卡片格式的 MessageSegment.json 消息
    参数：
        :param *text: 欢迎语
        :param icon: 图标的网址，若无则使用群头像
        :param tips: 卡片中的提示信息，若不为list则自动在外层包裹list
            :element tuple | list: [text, title]
                :element text: 提示文本, 标题默认为 `温馨提示`
                :element title: 当添加该值且不为空，则标题将被覆盖
            :element str: 提示文本，标题为 温馨提示
        :param buttons: 卡片中的按钮，若不为list则自动在外层包裹list
            :element tuple: [name, action]
                :element name: 按钮内容
                :element action: 按钮所需跳转的网址
    '''
    proc_tips, proc_btns = [], []
    if tips:
        for i in tips:
            title = '温馨提示'
            value = i
            if type(i) == type(()) or type(i) == type([]):
                value = i[0]
                try:
                    title = i[1] or title
                except:
                    pass
            proc_tips.append({
                'value': value,
                'title': title
            })
    if buttons:
        for i in buttons:
            proc_btns.append({
                'name': i[0],
                'action': i[1]
            })
    return ms.json({
        "app": "com.tencent.miniapp",
        "desc": "",
        "view": "notification",
        "ver": "0.0.0.1",
        "prompt": "入群欢迎",
        "meta": {
            "notification": {
                "appInfo": {
                    "appName": text,
                    "appType": 4,
                    "appid": 0,
                    "iconUrl": icon
                },
                "data": proc_tips,
                "title": "",
                "button": proc_btns,
                "emphasis_keyword": ""
            }
        }
    })


def image(
    path: str = None, b64: str = None
) -> ms:
    """
    说明：
        生成 MessageSegment.image 消息
        处理顺序 path > b64
    参数:
        :param path: 图片路径
        :param b64: 图片base64
    """
    if path:
        return (
            ms.image("file:///" + os.path.abspath(path))
            if os.path.exists(path)
            else ""
        )
    elif b64:
        return ms.image(b64 if "base64://" in b64 else "base64://" + b64)
    else:
        return ""


def at(qq: Union[int, str]) -> ms:
    """
    说明：
        生成一个 MessageSegment.at 消息
    参数：
        :param qq: qq号
    """
    return ms.at(qq)


def text(msg: str) -> ms:
    """
    说明：
        生成一个 MessageSegment.text 消息
    参数：
        :param msg: 消息文本
    """
    return ms.text(msg)


def face(id_: int) -> ms:
    """
    说明：
        生成一个 MessageSegment.face 消息
    参数：
        :param id_: 表情id
    """
    return ms.face(id_)
