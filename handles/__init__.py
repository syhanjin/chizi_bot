import pymongo

client = pymongo.MongoClient('127.0.0.1', 27017)
db = client['qbot']
userdb = client['user']


def make_query(group_id: str, user_id: str): return {
    'group_id': group_id, 'user_id': user_id}


class User:
    def __init__(self, group_id: str, user_id: str):
        self.group_id = group_id
        self.user_id = user_id
        data = db.user.find_one(make_query(group_id, user_id))
        if data == None:
            data = {}

        def _(k, v): return data[k] if(k in data) else v
        self.favor = _('favor', 0)
        self.favorLvl = _('favorLvl', 0)
        self.coin = _('coin', 0)
        self.sy = _('sy', None)
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
        self.user = None
        if user != None:
            self.user = user['user']
        if admin != None:
            self.admin = admin['admin']
        else:
            self.admin = 0
        return None

    def update_from_msg(self, msg):
        if msg == None or 'sender' not in msg:
            return False
        sender = msg['sender']
        self.card = (sender.get('card') or sender.get('nickname') or '用户名未识别')
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

    def update_from_event(self, event):
        sender = getattr(event, 'sender', None)
        if sender == None:
            return False
        self.card = getattr(sender, 'card', None) or getattr(
            sender, 'nickname', '用户名未识别')
        self.age = getattr(sender, 'age', None)
        self.sex = getattr(sender, 'sex', None)
        self.area = getattr(sender, 'area', None)
        self.level = getattr(sender, 'level', None)
        self.title = getattr(sender, 'title', None)
        self.role = getattr(sender, 'role', None)
        if self.role == 'admin':
            self.admin = 2
        elif self.role == 'owner':
            self.admin = 3
        return True
    
    def update_from_info(self, sender):
        if sender == None:
            return False
        self.card = getattr(sender, 'card', None) or getattr(
            sender, 'nickname', '用户名未识别')
        self.age = getattr(sender, 'age', None)
        self.sex = getattr(sender, 'sex', None)
        self.area = getattr(sender, 'area', None)
        self.level = getattr(sender, 'level', None)
        self.title = getattr(sender, 'title', None)
        self.role = getattr(sender, 'role', None)
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
            }, True
        )

    def add_favor(self, favor):
        self.favor = round(self.favor + favor, 2)
        if self.favor > self.fav_max:
            self.favorLvl += 1
