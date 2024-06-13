import torch
from TTS.api import TTS
import simpleaudio as sa

import requests
import json
import uuid
import base64
import pygame  # 引入pygame库
import os

class TtsServiceBase:
    def __init__(self):
        pass

    def speech(self, text):
        raise NotImplementedError("Subclasses should implement this method")

class TtsServiceOnline(TtsServiceBase):
    def __init__(self):
        super().__init__()
        self.appid = "3710583282"
        self.access_token = os.getenv("TTS_ACCESS_TOKEN")
        self.cluster = os.getenv("TTS_CLUSTER")
        self.voice_type = "BV001_streaming"
        self.host = "openspeech.bytedance.com"
        self.api_url = f"https://{self.host}/api/v1/tts"
        self.header = {"Authorization": f"Bearer;{self.access_token}"}

    def speech(self, text):
        request_json = {
            "app": {
                "appid": self.appid,
                "token": self.access_token,
                "cluster": self.cluster
            },
            "user": {
                "uid": "388808087185088"
            },
            "audio": {
                "voice_type": self.voice_type,
                "encoding": "mp3",
                "speed_ratio": 1.0,
                "volume_ratio": 1.0,
                "pitch_ratio": 1.0,
            },
            "request": {
                "reqid": str(uuid.uuid4()),
                "text": text,
                "text_type": "plain",
                "operation": "query",
                "with_frontend": 1,
                "frontend_type": "unitTson"
            }
        }
        try:
            resp = requests.post(self.api_url, json.dumps(request_json), headers=self.header)
            if "data" in resp.json():
                data = resp.json()["data"]
                file_to_save = open("output.mp3", "wb")
                file_to_save.write(base64.b64decode(data))
                file_to_save.close()
                # 使用pygame播放生成的MP3文件
                pygame.mixer.init()
                pygame.mixer.music.load("output.mp3")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():  # 等待音乐播放完成
                    pygame.time.Clock().tick(10)
                pygame.mixer.music.unload() 
        except Exception as e:
            print(f"Error: {str(e)}")

class TtsServiceLocal(TtsServiceBase):
    def __init__(self):
        super().__init__()
        # 获取设备
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        # 初始化 TTS
        self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)
    
    def speech(self, text):
        output_path = "output.wav"
        # 生成语音文件
        self.tts.tts_to_file(
            text=text, 
            speaker_wav="./clone.wav",
            language="zh", 
            file_path=output_path
        )
        # 播放生成的语音文件
        wave_obj = sa.WaveObject.from_wave_file(output_path)
        play_obj = wave_obj.play()
        play_obj.wait_done()


def CreateTtsService(service_type):
    if service_type == "online":
        return TtsServiceOnline()
    elif service_type == "local":
        return TtsServiceLocal()
    else:
        raise ValueError("Invalid service type. Choose 'online' or 'local'.")