
from nonebot.adapters.cqhttp.message import MessageSegment as ms





def welcome(text: str, icon: str='', tips: list=[], buttons: list=[]):
    '''
    text: str, 欢迎语
    
    icon: str, 图标的网址

    tips: list, 元素为一个字典
    - title:  提示类型，例：温馨提示
    - value:  提示内容

    buttons: list，元素为一个字典
    - name:   按钮内容
    - action: 按钮所需跳转的网址
    '''
    return ms.json({
        "app": "com.tencent.miniapp",
        "desc": "",
        "view": "notification",
        "ver": "0.0.0.1",
        "prompt": "欢迎入群",
        "meta": {
            "notification": {
                "appInfo": {
                    "appName": text,
                    "appType": 4,
                    "appid": 1234567890,
                    "iconUrl": icon
                },
                "data": tips,
                "title": "",
                "button": buttons,
                "emphasis_keyword": ""
            }
        }
    })