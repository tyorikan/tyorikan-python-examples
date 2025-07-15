
import os
import json
import re
import base64
from google import genai
from google.genai import types
from google.cloud import texttospeech
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

class VideoRequest(BaseModel):
    url: str

class AudioRequest(BaseModel):
    text: str
    voice: str = "ja-JP-Standard-A"  # デフォルトの日本語音声

YOUTUBE_URL_REGEX = re.compile(
    r"^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})"
)

# Vertex AI設定の確認
project_id = os.getenv("PROJECT_ID")
location = os.getenv("LOCATION")

if not project_id or project_id == "your-project-id":
    print("Warning: PROJECT_ID not set in .env file. Please configure Google Cloud credentials.")
    print("For now, the application will not work without proper Vertex AI configuration.")
    raise ValueError("PROJECT_ID and LOCATION must be set in .env file for Vertex AI")

client = genai.Client(
    vertexai=True,
    project=project_id,
    location=location
)

def get_transcript(video_id: str):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'ja'])
        return " ".join([item["text"] for item in transcript_list])
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        raise HTTPException(status_code=404, detail=f"Could not retrieve transcript for video ID {video_id}.")

def generate_audio(text: str, voice: str = "ja-JP-Standard-A", speaking_rate: float = 1.5):
    """テキストを音声に変換する"""
    try:
        # Google Cloud Text-to-Speechクライアントを初期化
        tts_client = texttospeech.TextToSpeechClient()
        
        # 音声合成のリクエストを設定
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        # 音声の設定
        voice_params = texttospeech.VoiceSelectionParams(
            language_code="ja-JP",
            name=voice
        )
        
        # オーディオの設定（話す速度を2倍に設定）
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=speaking_rate  # 1.5倍速
        )
        
        # 音声合成を実行
        response = tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice_params,
            audio_config=audio_config
        )
        
        # Base64エンコードして返す
        return base64.b64encode(response.audio_content).decode('utf-8')
    except Exception as e:
        print(f"Error generating audio (Google Cloud TTS not configured): {e}")
        # 認証エラーの場合はダミーデータを返す（開発用）
        print("Returning None - audio feature disabled without proper Google Cloud authentication")
        return None

@app.post("/summarize")
def summarize(request: VideoRequest):
    try:
        match = YOUTUBE_URL_REGEX.match(request.url)
        if not match:
            raise HTTPException(status_code=400, detail="Invalid YouTube URL provided.")
        
        video_id = match.group(4)
        transcript = get_transcript(video_id)

        prompt = f"""以下のYouTube動画のトランスクリプトを日本語で、動画の全体が分かるような文章量で要約してください。必要であれば長くて構いません。
また、英語学習者向けに重要となる、英語の語彙と文法のポイントも抽出し、例文なども踏まえて分かりやすく説明してください。
以下のスキーマを持つJSONオブジェクトのみで回答してください。:
{{
  "summary": "string",
  "english_learning": {{
    "vocabulary": [
      {{"word": "string", "example": "string"}}
    ],
    "grammar": [
      {{"rule": "string", "example": "string"}}
    ]
  }}
}}
 
Transcript:
{transcript}
"""
        response = client.models.generate_content(
          model='gemini-2.5-flash',
          contents=prompt,
          config=types.GenerateContentConfig(
            response_mime_type='application/json'
          )
        )

        try:
            response_json = json.loads(response.text)
            return JSONResponse(content=response_json)
        except (ValueError, json.JSONDecodeError):
            return JSONResponse(
                status_code=500,
                content={"detail": "Failed to process the video summary due to an invalid or empty response from the model."}
            )

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred while processing the video.")

@app.post("/summarize-with-audio")
def summarize_with_audio(request: VideoRequest):
    """要約とその音声を同時に返すエンドポイント"""
    try:
        match = YOUTUBE_URL_REGEX.match(request.url)
        if not match:
            raise HTTPException(status_code=400, detail="Invalid YouTube URL provided.")
        
        video_id = match.group(4)
        transcript = get_transcript(video_id)

        prompt = f"""以下のYouTube動画のトランスクリプトを日本語で、動画の全体が分かるような文章量で要約してください。必要であれば長くて構いません。
また、英語学習者向けに重要となる、英語の語彙と文法のポイントも抽出し、例文なども踏まえて分かりやすく説明してください。
以下のスキーマを持つJSONオブジェクトのみで回答してください。:
{{
  "summary": "string",
  "english_learning": {{
    "vocabulary": [
      {{"word": "string", "example": "string"}}
    ],
    "grammar": [
      {{"rule": "string", "example": "string"}}
    ]
  }}
}}
 
Transcript:
{transcript}
"""
        response = client.models.generate_content(
          model='gemini-2.5-flash',
          contents=prompt,
          config=types.GenerateContentConfig(
            response_mime_type='application/json'
          )
        )

        try:
            response_json = json.loads(response.text)
            
            # 要約テキストから音声を生成（認証が設定されている場合のみ）
            summary_text = response_json.get("summary", "")
            audio_base64 = generate_audio(summary_text)
            
            # 音声データが生成された場合のみレスポンスに追加
            if audio_base64:
                response_json["audio"] = audio_base64
            else:
                response_json["audio_error"] = "Audio generation not available - Google Cloud TTS not configured"
            
            return JSONResponse(content=response_json)
        except (ValueError, json.JSONDecodeError):
            return JSONResponse(
                status_code=500,
                content={"detail": "Failed to process the video summary due to an invalid or empty response from the model."}
            )

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred while processing the video.")

@app.post("/text-to-speech")
def text_to_speech_endpoint(request: AudioRequest):
    """テキストを音声に変換するエンドポイント"""
    try:
        audio_base64 = generate_audio(request.text, request.voice)
        if audio_base64 is None:
            raise HTTPException(status_code=500, detail="Failed to generate audio")
        
        return JSONResponse(content={"audio": audio_base64})
    except Exception as e:
        print(f"Error in text-to-speech endpoint: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while generating audio.")

app.mount("/", StaticFiles(directory="static", html=True), name="static")
