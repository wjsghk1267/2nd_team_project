import json
import csv
from tqdm import tqdm
from py.analysis_service import get_basic_llm, analyze_text
from langchain.vectorstores import MongoDBAtlasVectorStore
from langchain.retrievers import MergerRetriever

# 테스트 케이스 파일 경로
test_cases_file = 'test_cases.json'
results_file = 'test_results.csv'

# RAG를 위한 벡터 스토어 설정
vectorStore_pdf = MongoDBAtlasVectorStore('VectorStore_RAG_54.RAG_traffic_accidents_54', 'vector_index_1')
vectorStore_json1 = MongoDBAtlasVectorStore('VectorStore_RAG_Online.RAG_traffic_accidents_Online', 'vector_index_2')
vectorStore_json2 = MongoDBAtlasVectorStore('dbsparta.if_json', 'if_index')

# retriever 생성
retriever_pdf = vectorStore_pdf.as_retriever()
retriever_json1 = vectorStore_json1.as_retriever()
retriever_json2 = vectorStore_json2.as_retriever()

# MergerRetriever를 사용하여 모든 검색기 통합
merger_retriever_json = MergerRetriever(retrievers=[retriever_json1, retriever_json2])
merger_retriever_all = MergerRetriever(retrievers=[retriever_pdf, retriever_json1, retriever_json2])

def basic_llm_qa(query):
    llm = get_basic_llm()
    response = llm.predict(query)
    return response.strip()

def rag_llm_qa(retriever, query):
    # RAG를 사용하는 경우
    retrieved_docs = retriever.retrieve(query)
    context = " ".join([doc['content'] for doc in retrieved_docs])
    full_query = f"{query}\n\n{context}"
    result = analyze_text(full_query)
    return result.strip()

# 테스트 케이스 로드
with open(test_cases_file, 'r', encoding='utf-8') as f:
    test_cases = json.load(f)

# 결과 저장을 위한 CSV 파일 준비
with open(results_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
    fieldnames = ['query', 'basic_llm_response', 'rag_pdf_response', 'rag_json_response', 'rag_all_response', 'correct_answer']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    # 각 테스트 케이스에 대해 요청을 보내고 결과를 저장
    for case in tqdm(test_cases, desc="Processing test cases", unit="case"):
        query = case['query']
        correct_answer = case['correct_answer']
        
        # 기본 LLM 호출
        basic_llm_response = basic_llm_qa(query)
        
        # PDF만 사용하는 RAG 호출
        rag_pdf_response = rag_llm_qa(retriever_pdf, query)
        
        # JSON만 사용하는 RAG 호출
        rag_json_response = rag_llm_qa(merger_retriever_json, query)
        
        # PDF와 JSON 모두 사용하는 RAG 호출
        rag_all_response = rag_llm_qa(merger_retriever_all, query)
        
        # 결과 CSV에 저장
        writer.writerow({
            'query': query,
            'basic_llm_response': basic_llm_response,
            'rag_pdf_response': rag_pdf_response,
            'rag_json_response': rag_json_response,
            'rag_all_response': rag_all_response,
            'correct_answer': correct_answer
        })

print(f'Test results saved to {results_file}')
