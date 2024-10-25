import json
import csv
import os
from tqdm import tqdm
from py.analysis_service import get_basic_llm, analyze_text
from py.utils import model, OPENAI_API_KEY
from langchain_community.chat_models import ChatOpenAI  # Deprecation 경고 수정

# 테스트 케이스 파일 경로
test_cases_file = 'test_cases.json'
results_file = 'test_results.csv'

def basic_llm_qa(query):
    llm = get_basic_llm()
    response = llm.predict(query)
    return response.strip()

# 테스트 케이스 로드
with open(test_cases_file, 'r', encoding='utf-8') as f:
    test_cases = json.load(f)

# 결과 저장을 위한 CSV 파일 준비
with open(results_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
    fieldnames = ['query', 'basic_llm_response', 'analyze_text_response', 'correct_answer']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    # 각 테스트 케이스에 대해 요청을 보내고 결과를 저장
    for case in tqdm(test_cases, desc="Processing test cases", unit="case"):
        query = case['query']
        correct_answer = case['correct_answer']
        
        # basic_llm 호출
        basic_llm_response = basic_llm_qa(query)
        
        # analyze_text 호출
        analyze_text_response = analyze_text(query)  # analyze_text에서 생성된 답변 및 검색 결과
        
        # 결과 CSV에 저장
        writer.writerow({
            'query': query,
            'basic_llm_response': basic_llm_response,
            'analyze_text_response': analyze_text_response,
            'correct_answer': correct_answer
        })

print(f'Test results saved to {results_file}')
