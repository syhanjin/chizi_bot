import pymongo

client = pymongo.MongoClient('127.0.0.1', 27017)
db = client['qbot']
userdb = client['user']


def make_query(group_id: str, user_id: str): return {
    'group_id': group_id, 'user_id': user_id}


class User:
    async def __init__(self, group_id: str, user_id: str):
        self.group_id = group_id
        self.user_id = user_id
        data = db.user.find_one(make_query(group_id, user_id))
        await self.create(data)
        admin = db.admin.find_one({
            '$or': [
                make_query(group_id, user_id),
                {'user_id': user_id, 'admin': {'$gte': 4}}
            ]
        })
        fav = db.favlvl.find_one({'lvl': self.favorLvl})
        self.fav_max = fav['max']
        self.label = fav['label']
        self.attitude = fav['attitude']
        self.dfav = fav['fav']
        user = userdb.userdata.find_one({'qq': user_id})
        if user != None:
            self.user = user['user']
        if admin != None:
            self.admin = admin['admin']
        else:
            admin = 0
        return None

    async def create(self, data):
        if data == None:
            data = {}
        async def _(k, v): return data[k] if(k in data) else v
        self.favor = await _('favor', 0)
        self.favorLvl = await _('favorLvl', 0)
        self.coin = await _('coin', 0)
        self.sy = await _('sy', None)
        pass

    async def update_from_msg(self, msg):
        if msg == None or 'sender' not in msg:
            return False
        sender = msg['sender']
        self.card = sender['card'] if(
            'card' in sender) else sender.get('nickname')
        self.age = sender.get('age')
        self.sex = sender.get('sex')
        self.area = sender.get('area')
        self.level = sender.get('level')
        self.title = sender.get('title')
        self.role = sender.get('role')
        if self.role == 'admin':
            self.admin = 2
        elif self.role == 'owner':
            self.admin = 3
        return True

    async def save(self):
        db.user.update_one(
            make_query(self.group_id, self.user_id),
            {
                '$setOnInsert': make_query(self.group_id, self.user_id),
                '$set': {
                    'favor': self.favor,
                    'favorLvl': self.favorLvl,
                    'coin': self.coin,
                    'sy': self.sy,
                }
            },
            {'upsert': True}
        )
    
    async def add_favor(self, favor):
        self.favor += favor
        if self.favor > self.fav_max:
            self.favorLvl += 1
