import torch
import os
import numpy as np
import torch.nn as nn
import time
import torch.nn.functional as F
import torchaudio
import torchaudio.transforms as transforms
from torchaudio.transforms import MFCC
from torch.nn import TransformerEncoder, TransformerEncoderLayer

#selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from urllib.parse import quote

from playwright.sync_api import sync_playwright

import time
import pandas as pd
import random
from typing import Dict
import os
import glob
import re
import shutil
from pydub import AudioSegment

def mp_to_flac(download_dir):
    wav_files = glob.glob(os.path.join(download_dir, '*.mp3'))

        # 각 WAV 파일을 FLAC으로 변환 및 원본 WAV 파일 삭제
    for wav_file in wav_files:
        try:
            # WAV 파일 로드
            audio = AudioSegment.from_file(wav_file, format="mp3")

            # FLAC 파일명 생성 (확장자 변경)
            flac_file = os.path.splitext(wav_file)[0] + '.flac'

            # FLAC 파일로 저장
            audio.export(flac_file, format="flac")

            # FLAC 파일이 성공적으로 생성되면 원본 WAV 파일 삭제
            if os.path.exists(flac_file):
                os.remove(wav_file)
                print(f"Converted and deleted {wav_file}")

        except Exception as e:
            print(f"Error processing {wav_file}: {e}")

def preproc(song_name):
    root_dir = r'C:\Users\82103\Desktop\졸작\MBTI_Music\service\song_folder'
    download_directory = os.path.join(root_dir, song_name)
    mp_to_flac(download_directory)
    file_path = os.path.join(download_directory, song_name + ".flac")
    
    # mbti_labels = []
    # mbti_labels.append(np.array([1.0 if mbti_type == dir_name else 0.4 for mbti_type in mbti_types], dtype=np.float32).reshape(-1, 1))

    waveform, sr = torchaudio.load(file_path)
    waveform = torchaudio.transforms.Resample(orig_freq=sr, new_freq=8000)(waveform)

    # 스테레오 오디오를 모노로 변환
    if waveform.size(0) > 1:
        waveform = torch.mean(waveform, dim=0, keepdim=True)

    # MFCC 변환 설정 및 계산
    mfcc_transform = MFCC(sample_rate=8000, n_mfcc=20)
    mfcc = mfcc_transform(waveform)

    max_frame = 6000
    if mfcc.size(-1) > max_frame:
        mfcc = mfcc[:, :, :max_frame]
    elif mfcc.size(-1) < max_frame:
        mfcc = torch.nn.functional.pad(mfcc, (0, max_frame - mfcc.size(-1)))

    return mfcc.squeeze()  # 차원 축소

def download_song(song_name):
    root_dir = r'C:\Users\82103\Desktop\졸작\MBTI_Music\service\song_folder'
    download_path = os.path.join(root_dir, song_name)
    # 해당 경로에 폴더가 없으면 생성, 있으면 리턴
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    else:
        return 1
    
    with sync_playwright() as p:
        encoded_song_name = quote(song_name)
        url = f'https://www.youtube.com/results?search_query={encoded_song_name}'
        browser =  p.chromium.launch(headless=True)
        context =  browser.new_context(
            accept_downloads=True,
        )
        page =  context.new_page()
        
        page.goto(url)
        page.wait_for_timeout(5000)
        video_link =  page.get_attribute('a#video-title', 'href')
        video_link = "www.youtube.com" + video_link
    
        page.goto('https://ko.onlymp3.to/')
        page.fill('#txtUrl', video_link)
        page.wait_for_timeout(1000)
        page.click('#btnSubmit')
        page.wait_for_selector(".btn a", timeout=30000)
        
        try:
            with page.expect_download() as download_info:
                page.click(".btn a")  # 다운로드 버튼 클릭
                download =  download_info.value
                download.save_as(os.path.join(download_path,song_name + ".mp3"))

        except Exception as ex:
            print("Error during download process", ex)
            return 0
        
        while True:
            files=  os.listdir(download_path)
            try:
                files[0] =  1
                break
            except:
                pass
    
        browser.close()
        
    return 1


class MusicPreferenceTransformer(nn.Module):
    def __init__(self, input_dim, model_dim, num_heads, num_layers, num_mbti_types=16, seq_len=6000):
        super(MusicPreferenceTransformer, self).__init__()
        self.input_dim = input_dim
        self.model_dim = model_dim
        self.num_heads = num_heads
        self.num_layers = num_layers
        self.num_mbti_types = num_mbti_types
        self.seq_len = seq_len

        self.feature_embedding = nn.Linear(input_dim, model_dim)
        encoder_layer = TransformerEncoderLayer(d_model=model_dim, nhead=num_heads, batch_first=True)
        self.transformer_encoder = TransformerEncoder(encoder_layer, num_layers=num_layers)

        self.mbti_decoders = nn.ModuleList([
            nn.Sequential(
                nn.Linear(model_dim, model_dim),
                nn.ReLU(),
                nn.Linear(model_dim, 1),
                nn.ReLU()
            ) for _ in range(num_mbti_types)
        ])

        #  각 시퀀스 점수 통합
        self.sequence_integration = nn.ModuleList([
            nn.Sequential(
                nn.Linear(self.seq_len, model_dim),
                nn.ReLU(),
                nn.Linear(model_dim, 1),
                nn.Sigmoid()
            ) for _ in range(num_mbti_types)
        ])

    def forward(self, x):
        # x: [batch_size, input_dim, seq_len]
        x = x.permute(0, 2, 1)
        x = self.feature_embedding(x)  # [batch_size, seq_len, model_dim]
        x = self.transformer_encoder(x)  # [batch_size, seq_len, model_dim]

        # 각 MBTI 타입에 대한 선호도 계산
        mbti_preferences = [decoder(x) for decoder in self.mbti_decoders]  # List of [batch_size, seq_len, 1]
        mbti_preferences = torch.cat(mbti_preferences, dim=-1)  # [batch_size, seq_len, num_mbti_types]

        # 시퀀스에 대한 점수를 하나의 점수로 통합
        mbti_preferences = mbti_preferences.permute(0, 2, 1)  # [batch_size, num_mbti_types, seq_len]

        mbti_scores = []
        for i, integrator in enumerate(self.sequence_integration):
          integrated_score = integrator(mbti_preferences[:, i, :])  # Process each MBTI type separately
          mbti_scores.append(integrated_score)

        mbti_scores = torch.cat(mbti_scores, dim=1)  # [batch_size, num_mbti_types]

        return mbti_scores