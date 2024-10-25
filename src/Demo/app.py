# app.py
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from py.user_service import save_user, check_user
from py.utils import db_client, UPLOAD_FOLDER
from py.conversation import ConversationManager, chat_history_collection  # 이 부분을 추가
import os
import uuid
from py.analysis_service import analyze_text, analyze_video_with_interaction

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/save_conversations', methods=['POST'])
def save_conversations():
    global conversation_manager
    if conversation_manager is None:
        from py.conversation import ConversationManager, chat_history_collection
        conversation_manager = ConversationManager()
    
    message, status = conversation_manager.save_conversations(chat_history_collection)
    return jsonify({'message': message}), status


# 업로드 폴더 설정
app.config['UPLOAD_FOLDER'] = 'uploads/'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login_main')
def login_main():
    return render_template('login_main.html')

@app.route('/login', methods=['POST'])
def login():
    id = request.form['id']
    password = request.form['password']
    nickname = check_user(id, password)
    if nickname:
        session['nickname'] = nickname
        return redirect(url_for('index_login'))
    else:
        return "로그인 실패. 다시 시도해 주세요."

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        id = request.form['id']
        password = request.form['password']
        nickname = request.form['nickname']
        email = request.form['email']
        birthdate = request.form['birthdate']
        save_user(id, password, nickname, email, birthdate)
        return redirect(url_for('login_main'))
    return render_template('register.html')

@app.route('/index_login')
def index_login():
    nickname = session.get('nickname')
    if nickname:
        return render_template('index_login.html', nickname=nickname)
    return redirect(url_for('login_main'))

@app.route('/ask', methods=['POST'])
def ask():
    if 'video' in request.files:
        try:
            video_file = request.files['video']
            unique_filename = str(uuid.uuid4()) + os.path.splitext(video_file.filename)[1]
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            video_file.save(video_path)
            
            # analysis_service의 비디오 분석 함수 호출
            response_text = analyze_video_with_interaction(video_path)
            os.remove(video_path)
        except Exception as e:
            return jsonify({'answer': f"오류가 발생했습니다: {str(e)}"}), 500
    else:
        try:
            user_input = request.form['question']
            response_text = analyze_text(user_input)  # analyze_text 함수 사용
        except Exception as e:
            return jsonify({'answer': f"오류가 발생했습니다: {str(e)}"}), 500

    return jsonify({'answer': response_text})

@app.route('/logout')
def logout():
    session.pop('nickname', None)
    return redirect(url_for('index'))

# @app.route('/save_conversations', methods=['POST'])
# def save_conversations():
#     global all_conversations  # 전역 변수 사용 선언
#     try:
#         if all_conversations:
#             chat_history_collection.insert_one({"chat_history": all_conversations})
#             # 저장 후 리스트 초기화
#             all_conversations = []
#             return jsonify({'message': '대화 기록이 성공적으로 저장되었습니다.'}), 200
#         else:
#             return jsonify({'message': '대화 기록이 비어 있습니다.'}), 400
#     except Exception as e:
#         return jsonify({'message': f'저장 중 오류 발생: {str(e)}'}), 500



if __name__ == '__main__':
    app.run(port=9199)