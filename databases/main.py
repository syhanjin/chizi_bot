import datetime
import pymongo

client = pymongo.MongoClient('127.0.0.1', 27017)
db = client['qbot']

db.drop_collection('increase')
db.create_collection('increase')
db.increase.insert_many([
    {'group_id': 457263503, 'msg':'''欢迎新同学，请改名片：格式 [C/K+]班级[+学号]-名字'''}
])