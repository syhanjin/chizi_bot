
import pymongo

client = pymongo.MongoClient('127.0.0.1', 27017)
db = client['qbot']


class User:
    def __init__(self, group_id, user_id):
        self.__group_id = group_id
        self.__user_id = user_id
        data = db.user.find_one({'group_id': group_id, 'user_id': user_id})
        self.create(data)

        pass

    def create(self, data):
        if data == None:
            data = {}

        def _(k, v): return data[k] if(k in data) else v
        self.favor = _('favor', 0)
        self.coin = _('coin', 0)
        self.sy = _('sy', None)
        pass

    def save(self):
        db.user.update_one(
            {'group_id': self.__group_id, 'user_id': self.__user_id},
            {
                '$setOnInsert': {'group_id': self.__group_id, 'user_id': self.__user_id},
                '$set': {
                    'favor': self.favor,
                    'coin': self.coin,
                    'sy': self.sy,
                }
            },
            {'upsert': True}
        )
