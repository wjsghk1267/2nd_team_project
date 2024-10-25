// 질문 제출 폼에 대한 이벤트 리스너
document.getElementById('questionForm').addEventListener('submit', function (event) {
    event.preventDefault();
    var question = document.getElementById('question').value;

    fetch('/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: 'question=' + encodeURIComponent(question)
    })
    .then(response => response.json())
    .then(data => {
        // 응답을 받아 답변 영역에 표시
        document.getElementById('answerText').innerText = data.answer;
        document.getElementById('answer').classList.remove('hidden');
        
        // 채팅 메시지 영역에 질문과 답변을 추가합니다.
        addMessageToChat(question, data.answer);
        
        // 검색 기록을 localStorage에 저장
        saveSearchHistory(question);
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

// 검색 기록을 저장하는 함수
function saveSearchHistory(query) {
    let searchHistory = JSON.parse(localStorage.getItem('searchHistory')) || [];
    searchHistory.push(query);
    localStorage.setItem('searchHistory', JSON.stringify(searchHistory));
    updateSearchHistory();
}

// 검색 기록을 불러와 업데이트하는 함수
function updateSearchHistory() {
    const searchHistory = JSON.parse(localStorage.getItem('searchHistory')) || [];
    const searchHistoryList = document.getElementById('search-history');
    searchHistoryList.innerHTML = '';

    searchHistory.forEach(function(query, index) {
        let li = document.createElement('li');
        li.textContent = query;
        li.classList.add('search-item');
        searchHistoryList.appendChild(li);

        // 각 검색 기록 항목에 클릭 이벤트 추가
        li.addEventListener('click', function() {
            performSearch(query);
        });
    });
}

// 페이지 로드 시 검색 기록을 불러와 표시
document.addEventListener('DOMContentLoaded', function() {
    updateSearchHistory();
});

// 채팅 메시지 영역에 질문과 답변을 추가하는 함수
function addMessageToChat(question, answer) {
    const messagesDiv = document.getElementById('messages');

    messagesDiv.innerHTML += '<div class="message-container"><i class="fas fa-user icon user"></i><div class="user">' + question + '</div></div>';
    messagesDiv.innerHTML += '<div class="message-container"><i class="fas fa-robot icon bot"></i><div class="bot">' + answer + '</div></div>';
    
    messagesDiv.scrollTop = messagesDiv.scrollHeight; // 새로운 메시지가 추가되면 스크롤을 아래로
}

// 검색 기록에 기반한 동작을 수행하는 함수
function performSearch(query) {
    // 검색 기록 클릭 시 해당 질문을 다시 표시
    addMessageToChat(query, '이전 검색 결과를 다시 표시합니다. 잠시만 기다려주세요 ..');
}
