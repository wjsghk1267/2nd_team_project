# utils.py
import os
from pymongo import MongoClient

# MongoDB URI 설정
MONGODB_URI = ""
db_client = MongoClient(MONGODB_URI)
db = db_client['Test']
video_analysis_collection = db['video_analysis']
chat_history_collection = db['chat_log']

# 업로드 폴더 설정
UPLOAD_FOLDER = 'uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 환경 변수 설정
model = "gpt-4o-mini-2024-07-18"
OPENAI_API_KEY = ''
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY