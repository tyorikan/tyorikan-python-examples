
import os
import json
import re
from google import genai
from google.genai import types
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

YOUTUBE_URL_REGEX = re.compile(
    r"^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})"
)

client = genai.Client(
    vertexai=True,
    project=os.getenv("PROJECT_ID"),
    location=os.getenv("LOCATION")
)

def get_transcript(video_id: str):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'ja'])
        return " ".join([item["text"] for item in transcript_list])
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        raise HTTPException(status_code=404, detail=f"Could not retrieve transcript for video ID {video_id}.")

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

app.mount("/", StaticFiles(directory="static", html=True), name="static")
