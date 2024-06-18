import google.generativeai as genai
import os
import time
import sys
import json

from log import *
import config

api_key = os.getenv("GENAI_API_KEY") or config.GENAI_API_KEY
genai.configure(api_key=api_key)

class McBot:
    def __init__(self):
        generation_config = {
            "temperature": 0.9,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 512,
            "response_mime_type": "text/plain",
        }
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE",
            }
        ]
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-latest",
            system_instruction=self._make_system_instruction(),
            safety_settings=safety_settings,
            generation_config=generation_config,
        )
        self.chat_session = self.model.start_chat()
        self.max_history = 50
        self._last_response = ""

    def _make_system_instruction(self):
        content = "接下来我们开始玩minecraft这个游戏"
        try:
            with open('mc_cookbook.txt', 'r', encoding='utf-8') as file:
                content = file.read()
                return f"```{content}``` 上面是minecraft的部分合成配方供你参考。接下来需要你一步一把教我怎么玩这个游戏"
        except FileNotFoundError:
            print_color("文件未找到", RED)
        except Exception as e:
            print_color(f"读取文件时发生错误: {str(e)}", RED)
        return content
        

    def upload_to_gemini(self, path, mime_type=None):
        """Uploads the given file to Gemini."""
        file = genai.upload_file(path, mime_type=mime_type)
        return file

    def wait_for_files_active(self, *files):
        """Waits for the given files to be active."""
        for name in (file.name for file in files):
            file = genai.get_file(name)
            while file.state.name == "PROCESSING":
                print(".", end="", flush=True)
                time.sleep(1)
                file = genai.get_file(name)
            if file.state.name != "ACTIVE":
                raise Exception(f"File {file.name} failed to process")
            
    def random_chat_style(self):
        import random
        styles = [
            "温和的",
            "扮演我的爱人，温情脉脉地，煽情地，温柔的,想和我在一起",
            "尖酸刻薄",
            "嘲讽的",
            "正面的，鼓励的",
            "闲聊的",
            "暴躁地,羞辱和骂我玩得很差，但是还是会给出答案"
        ]
    
        return random.choice(styles)

    def chat(self, message, video_file_path):
        try:
            video_file = self.upload_to_gemini(video_file_path, mime_type="video/mp4")
            self.wait_for_files_active(video_file)
            
            prompt = f"接下来请用<{self.random_chat_style()}>的语态和我对话, 不要超过1句话\n"
            #print(prompt)
            
            if message:
                prompt += f'''
                    观察游戏录屏，回答下面这个问题 
                    ```
                    {message}
                    ```
                    '''
            else:
                prompt += f'''
                    观察游戏录屏，则根据画面内容进行评论
                    '''
            response = self.chat_session.send_message([video_file, prompt])
            history = self.chat_session.history
            if len(history) > self.max_history:
                history = history[2:]
                self.chat_session.history = history
            
            self._last_response = response.text
            return response.text
        except Exception as e:
            #print(f"\033[91m处理过程中发生错误: {str(e)}\033[0m")
            print(f"---")
            
    @property
    def last_response(self):
        resp = self._last_response
        self._last_response = ""
        return resp
