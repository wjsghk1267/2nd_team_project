# retriever.py
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import MongoDBAtlasVectorSearch
from langchain.retrievers import MergerRetriever
from langchain.prompts import ChatPromptTemplate
from langchain.prompts import MessagesPlaceholder
from pymongo import MongoClient
from openai import OpenAI
import os
from .utils import OPENAI_API_KEY, MONGODB_URI

# MongoDB 연결 설정
db_client = MongoClient(MONGODB_URI)

# OpenAI API 키 설정
client = OpenAI(api_key=OPENAI_API_KEY)

def get_ret():
    # 임베딩 모델 설정
    model_name = "BAAI/bge-m3"
    model_kwargs = {"device": "cpu"}
    encode_kwargs = {"normalize_embeddings": True}
    embeddings_model = HuggingFaceEmbeddings(
        model_name=model_name, 
        model_kwargs=model_kwargs, 
        encode_kwargs=encode_kwargs
    )
    
    # # MongoDB Atlas에서 첫 번째 벡터 스토어 불러오기
    # index_name = 'vector_index_1'
    # dbName = "VectorStore_RAG_54"
    # collectionName = "RAG_traffic_accidents_54"
    # collection = db_client[dbName][collectionName]

    # vectorStore1 = MongoDBAtlasVectorSearch(
    #     embedding=embeddings_model,
    #     collection=collection,
    #     index_name=index_name
    # )

    # general json 자료
    index_name_json = 'general_index'
    dbName_json = "dbsparta"
    collectionName_json = "general_json"
    collection_json = db_client[dbName_json][collectionName_json]

    vectorStore_json1 = MongoDBAtlasVectorSearch(
        embedding=embeddings_model,
        collection=collection_json,
        index_name=index_name_json,
        embedding_key="vector",  # JSON 문서에서 벡터 필드의 키
        text_key="accidentDetails"  # JSON 문서에서 텍스트 필드의 키
    )

    # if json 자료
    index_name_json = 'if_index'
    dbName_json = "dbsparta"
    collectionName_json = "if_json"
    collection_json = db_client[dbName_json][collectionName_json]

    vectorStore_json2 = MongoDBAtlasVectorSearch(
        embedding=embeddings_model,
        collection=collection_json,
        index_name=index_name_json,
        embedding_key="vector",  # JSON 문서에서 벡터 필드의 키
        text_key="accidentOverview"  # JSON 문서에서 텍스트 필드의 키
    )

    # 각 vectorstore에서 retriever를 생성
    # retriever1 = vectorStore1.as_retriever()
    retriever_json1 = vectorStore_json1.as_retriever()
    retriever_json2 = vectorStore_json2.as_retriever()
    
    # MergerRetriever를 사용하여 모든 검색기 통합
    merger_retriever = MergerRetriever(retrievers=[retriever_json1, retriever_json2])
    
    return merger_retriever

# Prompt templates
system_template = ChatPromptTemplate.from_messages(
    messages=[
        ('system',
            """
            role : You are an experienced lawyer with over 20 years of experience in traffic law. 
            Communication method: Please communicate with users in Korean.
            Provide professional and practical legal advice on traffic accident inquiries. 
            Consider the situation description and provide detailed answers, including:
            1. Fault ratio for the accident.
            2. Main issues in the accident situation.
            3. Reasons and basis for the decision.
            4. Relevant legal clauses and interpretation.
            5. Specific resolution or legal procedure guidance.
            6. Legal risks or considerations to be aware of.
            7. Summarized conclusion of the above content.
            Please think in order and answer.

            \n\n
            Context: {context}
            """),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
    ]
)

# Video analysis chain
video_template = ChatPromptTemplate.from_messages(
    messages=[
        ('system',
            """
Analyze the following video content:
Frames: {frames}
Audio transcript: {audio_transcript}

Provide a detailed analysis of the traffic accident shown in the video, including:
1. Accident situation: Describe the accident from the driver's perspective, from start to finish.
2. Accident analysis: Analyze the external factors that caused the accident from the driver's perspective.
3. Main issues: Based on the analysis, identify the faults of each party and the core issues of the incident.
4. Fault ratio: Determine the fault ratio based on traffic laws.
\n\n
            Context: {context}
            """),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
    ]
)