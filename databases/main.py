import datetime
import pymongo

client = pymongo.MongoClient('127.0.0.1', 27017)
db = client['qbot']

db.drop_collection('increase')
db.create_collection('increase')
db.increase.insert_many([
    {
        'group_id': 457263503,
        'type': 'card',
        'icon': 'https://sakuyark.com/static/images/yyicon.jpg',
        'tips': [('请仔细查看公告内的群规',), ('格式 [C/K+]班级[+学号]-名字', '名片格式')],
        'text': '''欢迎新同学''',
        'opened': True
    },{
        'group_id': 1003132999,
        'type': 'card',
        'tips': [('请仔细查看公告内的群规',), ('格式 [C/K+]班级[+学号]-名字', '名片格式')],
        'text': '''欢迎新同学''',
        'opened': True
    }
])
