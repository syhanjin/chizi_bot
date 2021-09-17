
from re import S
import pymongo

client = pymongo.MongoClient('127.0.0.1', 27017)
db = client['qbot']
userdb = client['user']


def make_query(user_id: str): return {'group_id': 0, 'user_id': str(user_id)}


class User():
    def __init__(self, user_id):
        self.user_id = user_id
        data = db.user.find_one(make_query(user_id))
        if data is None:
            data = {}

        def _(k, v): return data[k] if(k in data) else v

        self.class_ = _('class', None)
        self.number = _('number', None)
        self.name = _('name', None)

        admin = db.admin.find_one(
            {'user_id': user_id, 'admin': {'$gte': 4}}
        )
        user = userdb.userdata.find_one({'qq': user_id})
        self.user = None
        if user != None:
            self.user = user['user']
        if admin != None:
            self.admin = admin['admin']
        else:
            self.admin = 0
        return None

    def update_from_event(self, event):
        sender = getattr(event, 'sender', None)
        if sender is None:
            return False
        self.sex = sender.sex
        self.age = sender.age
        self.nickname = sender.nickname
        return True

    async def set_class(self, school, class_, number, name):
        data = db.class_.find_one({
            'school': school,
            'class': class_,
            'number': number,
            'name': name
        })
        if data is None:
            return False
        self.class_ = class_
        self.number = number
        self.name = name
        return True

    async def save(self):
        db.user.update_one(
            make_query(self.user_id),
            {
                '$setOnInsert': make_query(self.user_id),
                '$set': {
                    'SC-YY': self.SCYY,
                    'class': self.class_,
                    'number': self.number,
                    'name': self.name
                }
            }, True
        )
