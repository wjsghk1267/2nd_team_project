# user_service.py
from pymongo import MongoClient
from .utils import db_client

# MongoDB 연결 설정
db = db_client['Test']
user_collection = db['user']

def save_user(id, password, nickname, email, birthdate):
    user_data = {
        "id": id,
        "password": password,
        "nickname": nickname,
        "email": email,
        "birthdate": birthdate
    }

def check_user(id, password):
    user = user_collection.find_one({"id": id, "password": password})
    if user:
        return user['nickname']
    return None
