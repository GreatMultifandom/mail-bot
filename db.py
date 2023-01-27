from pymongo import MongoClient

class Database:
    def __init__(self, mongo_url):
        self.client = MongoClient(mongo_url)
        self.db = self.client['mailu']
        self.users = self.db.users

    def form_user(self, tg_id: int):
        return {
            '_id': tg_id,
            'email': None
        }

    def set_email(self, tg_id, email):
        self.users.update_one({'_id': tg_id}, {"$set": {'email': email}})
    
    def create_user(self, tg_id):
        form = self.form_user(tg_id)
        self.users.insert_one(form)
        return form

    def get_user(self, tg_id):
        return self.users.find_one({'_id': tg_id})

    def process_user(self, tg_id: int):
        user = self.get_user(tg_id)
        if not user:
            user = self.create_user(tg_id)
            return user, 0 # new user
        elif not user['email']:
            return user, 1 # no email
        else:
            return user, 2 # user with email
        
