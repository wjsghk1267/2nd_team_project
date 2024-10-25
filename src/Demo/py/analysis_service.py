# analysis_service.py
from .utils import db_client, video_analysis_collection, OPENAI_API_KEY, model
from .retriever import get_ret, system_template, video_template
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from moviepy.editor import VideoFileClip
from pymongo import MongoClient
from openai import OpenAI
from .conversation import ConversationManager, chat_history_collection  # 이 부분을 추가
import base64
import cv2
import os

client = OpenAI(api_key=OPENAI_API_KEY)
conversation_manager = ConversationManager()

def get_basic_llm():
    return ChatOpenAI(
        model=model,
        temperature=0.3,
        openai_api_key=os.environ['OPENAI_API_KEY']
    )

# def load_memory(_):
#     return memory.load_memory_variables({})["chat_history"]
def load_memory(memory):
    chat_history = memory.load_memory_variables({})["chat_history"]
    return [msg.content for msg in chat_history]



def translate_text(text):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "너는 영어를 한국어로 통역해주는 통역가야"},
            {"role": "user", "content": text}
        ],
        max_tokens=500,
        # n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()

def analyze_text(question):
    from .conversation import ConversationManager, chat_history_collection
    try:
        # LLM 및 메모리 초기화
        memory = ConversationSummaryBufferMemory(
            llm=get_basic_llm(),
            max_token_limit=5000,
            return_messages=True,
            memory_key="chat_history"  # 메모리 변수를 일치시킵니다.
        )
        conversation_manager = ConversationManager()

        if not question or question.strip() == "":
            raise ValueError("질문이 제공되지 않았습니다.")   
        
        chain = (
            {
                "context": get_ret(),
                "question": RunnablePassthrough(),
                "chat_history": RunnableLambda(lambda _: load_memory(memory))
            }
            | system_template
            | get_basic_llm()
        )

        result = chain.invoke(question)

        # 메모리에 대화 기록 저장
        memory.save_context({"user": question}, {"AI_Model": str(result)})

        # 메모리에서 실시간으로 요약한 대화 기록 추출
        chat_history = memory.load_memory_variables({})["chat_history"]

        # 요약된 대화 기록을 문자열로 변환
        chat_history_str = "".join([msg.content for msg in chat_history])
        
        # 요약된 대화 기록을 한국어로 번역
        # chat_history_kor = translate_text(chat_history[0].content)
        chat_history_kor = translate_text(chat_history_str)
        
        # 질문과 응답을 리스트에 추가
        chat_data = {
            "user": question,
            "AI_Model": str(result),
            "summary": chat_history_kor
        }
        conversation_manager.add_conversation(chat_data)

        return result.content
                    
    except Exception as e:
        print(f"텍스트 분석 중 오류가 발생했습니다: {str(e)}")
        return f"오류 발생: {str(e)}"

def analyze_video(file_path, seconds_per_frame=2):
    base64Frames = []
    base_video_file, _ = os.path.splitext(file_path)
    video = cv2.VideoCapture(file_path)
    if not video.isOpened():
        raise Exception("Error opening video file")
    
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = video.get(cv2.CAP_PROP_FPS)
    frames_to_skip = int(fps * seconds_per_frame)
    
    curr_frame = 0
    while curr_frame < total_frames - 1:
        video.set(cv2.CAP_PROP_POS_FRAMES, curr_frame)
        success, frame = video.read()
        if not success:
            break
        
        _, buffer = cv2.imencode(".jpg", frame)
        base64Frames.append(base64.b64encode(buffer).decode("utf-8"))
        curr_frame += frames_to_skip
    
    video.release()

    clip = VideoFileClip(file_path)
    audio_path = f"{base_video_file}.mp3"
    try:
        if clip.audio:
            clip.audio.write_audiofile(audio_path, bitrate="32k")
            clip.audio.close()
        else:
            audio_path = None
    except Exception as e:
        audio_path = None
    clip.close()
    
    return base64Frames, audio_path

def summarize_video(base64Frames, audio_path):
    summary_text = ""
    if audio_path is not None:
        transcription = client.Audio.transcribe(
            model="whisper-1",
            file=open(audio_path, 'rb')
        )
        summary_text += transcription['text'] + "\n"

        response_both = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": video_template},
                {"role": "user", "content": f"이건 비디오 영상의 오디오 텍스트: {transcription['text']}"},
                {"role": "user", "content": "이 영상은 오디오와 함께 여러 프레임을 포함하고 있습니다. 여기에는 프레임 이미지가 포함되지만 텍스트 설명만 제공합니다."}
            ],
            temperature=0.3,
            top_p=0.9
        )
        summary_text += response_both.choices[0].message.content + "\n"
    else:
        response_vis = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": video_template},
                {"role": "user", "content": "이건 오디오가 없는 비디오 영상입니다. 아래 프레임을 기반으로 분석했습니다.  프레임 이미지가 포함되지만 텍스트 설명만 제공합니다."}
            ],
            temperature=0.3,
            top_p=0.9
        )
        summary_text += response_vis.choices[0].message.content + "\n"
    
    return summary_text

def analyze_video_with_interaction(file_path):
    base64Frames, audio_path = analyze_video(file_path, seconds_per_frame=2)
    video_summary = summarize_video(base64Frames, audio_path)
    # 영상 분석 결과 저장
    analysis_data = {
        "file_path": file_path,
        "summary": video_summary
    }
    video_analysis_collection.insert_one(analysis_data)
    return video_summary