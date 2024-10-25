from pymongo import MongoClient

class ConversationManager:
    def __init__(self):
        self.all_conversations = []

    def add_conversation(self, chat_data):
        self.all_conversations.append(chat_data)

    def save_conversations(self, chat_history_collection):
        if self.all_conversations:
            chat_history_collection.insert_one({"chat_history": self.all_conversations})
            self.all_conversations = []
            return '대화 기록이 성공적으로 저장되었습니다.', 200
        else:
            return '대화 기록이 비어 있습니다.', 400

# MongoDB 연결 설정
url = f"mongodb+srv://yoonsun2596:qwer1234@tm2.hl7a3.mongodb.net/"
db_client = MongoClient(url)
db = db_client['Test']
chat_history_collection = db['users']