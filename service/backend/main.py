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
from models import Base, MBTIMusic, SessionLocal, engine

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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class MusicCreate(BaseModel):
    mbti: str
    song_title: str
    artist: str
    img_src = str
    score: int
    
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 프론트엔드 서버 주소
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메소드 허용
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
)

def save_recommendation_to_db(mbti_scores: dict, song_name: str, singer: str, img_src: str, db: Session):
    # MBTI 점수를 데이터베이스에 저장
    for mbti, score in mbti_scores.items():
        # 동일한 노래에 대한 기존 데이터가 있는지 확인
        db_song = db.query(MBTIMusic).filter(MBTIMusic.song_title == song_name, MBTIMusic.artist == singer, MBTIMusic.mbti == mbti).first()
        if db_song:
            # 기존 데이터가 있다면 점수 업데이트
            db_song.score = score
        else:
            # 새로운 레코드 생성
            new_song = MBTIMusic(mbti=mbti, song_title=song_name, artist=singer, score=score, img_src=img_src)
            db.add(new_song)
    db.commit()


# mbti 들어왔을 때 점수 높은 노래들 반환
@app.get("/songs/{mbti}")
def read_top_songs(mbti: str, db: Session = Depends(get_db)):
    top_songs = db.query(MBTIMusic).filter(MBTIMusic.mbti == mbti).order_by(MBTIMusic.score.desc()).limit(20).all()
    return top_songs


#노래들어왔을때, 기반으로 BEST MBTI를 추천
@app.post("/recommend/")
def recommend(song_name: str = Form(...), singer: str = Form(...), img_src : str = Form(...), db: Session = Depends(get_db)):
    existing_songs = db.query(MBTIMusic).filter(MBTIMusic.song_title == song_name, MBTIMusic.artist == singer).all()
    
    if(existing_songs):
        return {song.mbti: song.score for song in existing_songs}
        
    else:
        query = song_name + "_" + singer
        get_song = download_song(query)
        if get_song == 0:
            raise HTTPException(status_code=404, detail="Download failed")
        
        song_vector = preproc(query)
        
        with torch.no_grad():
            output = model(song_vector.unsqueeze(0)).squeeze()
            
        output_list = output.tolist()
        scores_dict = {mbti: score for mbti, score in zip(mbti_types, output_list)}
        save_recommendation_to_db(scores_dict, song_name, singer, img_src, db)
        
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
        reload=False,
        port=8000
    )