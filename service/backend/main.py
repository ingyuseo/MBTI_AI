from fastapi import FastAPI, Depends,UploadFile, File, Form, HTTPException
from typing import Optional
from util_model import MusicPreferenceTransformer, download_song, preproc
from fastapi.middleware.cors import CORSMiddleware
import torch
from sqlalchemy.orm import Session

from pydantic import BaseModel

import os, sys
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import uvicorn
from ..db.models import Base, MBTIMusic, SessionLocal, engine

#### spotify api keys
cid = 'ecd654ce83084fad9d37d9f05bb169e8'
secret = '31142deadb7e4300901f2179ea5c7429'
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)

####### Server Component, Model, Selenium driver, CORS ###############################
app = FastAPI()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
mbti_types = ["INTP", "INTJ", "INFP", "INFJ", "ISTP", "ISTJ", "ISFP", "ISFJ", "ENTP", "ENTJ", "ENFP", "ENFJ", "ESTP", "ESTJ", "ESFP", "ESFJ"]

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = MusicPreferenceTransformer(input_dim=20, model_dim=256, num_heads=4, num_layers=4, num_mbti_types=16).to(device)

state_dict = torch.load('./service/backend/my_model_two.pth', map_location=torch.device('cpu'))
model.load_state_dict(state_dict)
model.eval()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 프론트엔드 서버 주소
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메소드 허용
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
)
# MBTI를 기반으로 노래를 추천하는 API
@app.post("/recommend/")
def recommend(song_name: str = Form(...), singer: str = From(...)):
    query = song_name + "_" + singer
    get_song = download_song(query)
    if get_song == 0:
        raise HTTPException(status_code=404, detail="Download failed")
    
    song_vector = preproc(query)
    
    with torch.no_grad():
        output = model(song_vector.unsqueeze(0)).squeeze()
        
    output_list = output.tolist()
    scores_dict = {mbti: score for mbti, score in zip(mbti_types, output_list)}

    return scores_dict


@app.post("/spotify_search/")
async def evaluate_song(song_info: str = Form(...)):
    search_num = 15 
    result = sp.search(song_info, limit=search_num, type="track")
    result_list = []
    for i in range(search_num):
        result_list.append( {"song_name":result['tracks']['items'][i]['name'],
            "singer" : result['tracks']['items'][i]['artists'][0]['name'],
            "album_img" : result['tracks']['items'][i]['album']['images'][0]['url']}
            )

    return result_list

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        reload=True,
        port=8000
    )