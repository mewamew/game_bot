import pyaudio
import webrtcvad
import wave
import whisper
import numpy as np
from log import *
import time

class Transcriber:
    def __init__(self, model_size="small"):
        print("Loading model...")
        self.model = whisper.load_model(model_size)

    def transcribe_audio(self, filename):
        # 加载音频并进行填充/修剪以适应30秒
        audio = whisper.load_audio(filename)
        audio = whisper.pad_or_trim(audio)

        # 制作log-Mel频谱图并移动到与模型相同的设备
        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)

        # 检测所说的语言
        _, probs = self.model.detect_language(mel)
        detected_language = max(probs, key=probs.get)

        # 解码音频
        options = whisper.DecodingOptions()
        result = whisper.decode(self.model, mel, options)

        # 返回识别的文本和语言
        return result.text, detected_language


class SpeechDetector:
    def __init__(self, filter="zh"):
        # 麦克风参数
        self.CHUNK_DURATION_MS = 30  # 每个块的持续时间（毫秒）
        self.CHUNK = int(16000 * self.CHUNK_DURATION_MS / 1000)  # 每个块的样本数
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.MAX_FRAMES = 300
        self.MAX_SILENCE_DURATION = 30 #秒
        self.filter = filter

        # 初始化VAD
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(0)  # 0-3, 3最敏感

        self.transcriber = Transcriber()

    def is_speaking(self, data):
        return self.vad.is_speech(data, self.RATE)

    def save_audio(self, frames, filename):
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(frames))

    def listen_and_transcribe(self):
        frames = []
        speaking = False
        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK)

        start_time = time.time()
        try:
            consecutive_speaking_frames = 0
            consecutive_silence_frames = 0
            speaking_threshold = 15
            silence_threshold = 30
            total_silence_duration = 0
            
            while True:
                if time.time() - start_time > 1:
                    start_time = time.time()
                    print("...")
                    
                data = stream.read(self.CHUNK)
                frames.append(data)
                frames = frames[-self.MAX_FRAMES:]
                total_silence_duration += self.CHUNK_DURATION_MS / 1000
                
                if self.is_speaking(data):
                    consecutive_speaking_frames += 1
                    consecutive_silence_frames = 0
                else:
                    consecutive_silence_frames += 1
                    consecutive_speaking_frames = 0
                    

                if not speaking:
                    if consecutive_speaking_frames >= speaking_threshold:
                        speaking = True
                        frames = frames[-30:]
                
                if speaking:
                    # 检测到连续静音，认为说话结束了
                    if consecutive_silence_frames >= silence_threshold:
                        filename = "output.wav"
                        self.save_audio(frames, filename)
                        text, language = self.transcriber.transcribe_audio(filename)
                        if text and language == self.filter:
                            #print(f"识别文本: {text}")
                            #print(f"检测到的语言: {language}")
                            return text, language

                        speaking = False
                        frames = []
                        consecutive_silence_frames = 0

                # 如果总静音时间超过MAX_SILENCE_DURATION，返回None和"zh"
                if total_silence_duration > self.MAX_SILENCE_DURATION:
                    #print("太长时间没说话，返回None")
                    return None, "zh"

        except KeyboardInterrupt:
            stream.stop_stream()
            stream.close()
            p.terminate()
            print("退出程序")
            return None,None
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()


if __name__ == "__main__":
    detector = SpeechDetector()
    while True:
        print("开始监听")
        text, language = detector.listen_and_transcribe()
        print("---")
        print(f"识别文本: {text}")
        print(f"检测到的语言: {language}")
