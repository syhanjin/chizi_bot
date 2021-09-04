import datetime
import pymongo

client = pymongo.MongoClient('127.0.0.1', 27017)
db = client['qbot']

db.drop_collection('cards')
db.create_collection('cards')
db.cards.insert_many([
    {
        'group_id': 457263503,
        'reg': '[ck]?(\d{2})?(\d{2})',
        'special': [2493288137, 1661800834, 2392160184, 3304119344, 1732085634, 2854196310, 1589876974, 3334913831, 3212043948],
        'format': '[C/K+]班级[+学号]-名字'
    }
])
