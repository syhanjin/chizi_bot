
from nonebot.adapters.cqhttp.message import MessageSegment as ms


def welcome(text: str, icon: str = '', tips: list = [], buttons: list = []):
    '''
    text: str, 欢迎语

    icon: str, 图标的网址

    tips: list, 元素为一个 元组: (text, [title])
    - text: 提示文本, 标题默认为 温馨提示
    - title: 当添加该值，则标题将被覆盖

    buttons: list，元素为一个 元组: (name, action)
    - name:   按钮内容
    - action: 按钮所需跳转的网址
    '''
    proc_tips, proc_btns = [], []
    for i in tips:
        proc_tips.append({
            'value': i[0],
            'title': '温馨提示' if (len(i) == 1) else i[1]
        })
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
        "prompt": "欢迎入群",
        "meta": {
            "notification": {
                "appInfo": {
                    "appName": text,
                    "appType": 4,
                    "appid": 1234567890,
                    "iconUrl": icon
                },
                "data": proc_tips,
                "title": "",
                "button": proc_btns,
                "emphasis_keyword": ""
            }
        }
    })
