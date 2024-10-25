/* 서버 백엔드 파일 */

const express = require('express');
const bodyParser = require('body-parser');
const path = require('path');
const mysql = require('mysql');

const app = express();

// MySQL 데이터베이스 연결 설정
const db = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: 'password',
    database: 'chatbot_db'
});

db.connect((err) => {
    if (err) throw err;
    console.log('Connected to database');
});

// bodyParser 설정
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

// 정적 파일 제공 (HTML, CSS, JS)
app.use(express.static(path.join(__dirname, 'public')));

// 사용자가 질문을 입력하면 이 경로로 POST 요청이 전송됨
app.post('/ask', (req, res) => {
    const question = req.body.question;

    // 여기서 챗봇 응답 생성 (간단한 예시로 Echo)
    const answer = `입력하신 질문: "${question}"에 대한 법률적 조언입니다...`;

    // 메시지와 응답을 데이터베이스에 저장
    const query = "INSERT INTO chat_log (user_message, bot_reply) VALUES (?, ?)";
    db.query(query, [question, answer], (err, result) => {
        if (err) throw err;
        console.log('Message saved to database');
        res.json({ answer: answer });
    });
});

// 서버 실행
app.listen(3000, () => {
    console.log('Server running on port 3000');
});
