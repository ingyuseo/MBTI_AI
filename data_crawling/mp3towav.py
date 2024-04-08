import os
import glob
from pydub import AudioSegment

# 현재 디렉토리의 모든 하위 디렉토리를 순회
for subdir in next(os.walk('.'))[1]:
    # 각 하위 디렉토리에서 WAV 파일 찾기
    wav_files = glob.glob(os.path.join(subdir, '*.wav'))

    # 각 WAV 파일을 FLAC으로 변환 및 원본 WAV 파일 삭제
    for wav_file in wav_files:
        try:
            # WAV 파일 로드
            audio = AudioSegment.from_file(wav_file, format="wav")

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