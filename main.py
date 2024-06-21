# Third-party libs
from speech_detector import SpeechDetector
from tts_service import CreateTtsService
from screen_recorder import ScreenRecorder
import shutil
import os
import subprocess
from flask import Flask, request, jsonify
import logging
import requests 
import sys
import argparse
import pygetwindow as gw

# First-party libs
from log import *
from bot import McBot
import config

DEFAULT_WINDOW = "Minecraft" # Default to play Minecraft
DEFAULT_TTS_MODE = "local"  # Default TTS mode

def parse_arguments():
    parser = argparse.ArgumentParser(description="启动参数")
    parser.add_argument('--window', type=str, default=DEFAULT_WINDOW, help='监听的窗口名称')
    parser.add_argument('--tts', type=str, default=DEFAULT_TTS_MODE, choices=['online', 'local'], help='TTS 模式 (online 或 local)')
    parser.add_argument('--list-windows', action='store_true', help='列出当前所有窗口')
    return parser.parse_args()

def list_windows():
    windows = gw.getAllTitles()
    for window in windows:
        if window:
            print(window)

if __name__ == "__main__":
    print_color("=== 🐱 仅供娱乐，无任何实用价值 🐱===", RED)
    
    args = parse_arguments()
    
    if args.list_windows:
        list_windows()
        sys.exit(0)

    wait_for_window = args.window or config.GENAI_API_KEY
    tts_mode = args.tts or config.TTS_MODE

    
    # Environment cleanup
    # Delete the output_videos folder
    output_dir = "output_videos"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    
    bot = McBot()
    
    # If playing Minecraft, also enable an in-game bot
    # Run node bot.js
    if wait_for_window == "Minecraft":
        subprocess.Popen(["node", "bot.js"])
    
    speech_detector = SpeechDetector()
    tts_helper = CreateTtsService(tts_mode)
    
    recorder = ScreenRecorder()
    recorder.wait_for_window(wait_for_window)
    recorder.start_recording()

    while True:
        # Detect speech
        print_color("......", GREEN)
        message, language = speech_detector.listen_and_transcribe()
        if not message and not language:
            print("Stop screen recording")
            recorder.stop_recording()

            print("Goodbye!")
            break
        if language == "zh":
            if message:
                print_color(f"👧 says: {message}", BLUE)
                
            recorder.stop_recording()
            video_file = recorder.fetch_record()
            retry_count = 0
            max_retries = 3
            response = ""
            while retry_count < max_retries and not response:
                response = bot.chat(message, video_file)
                retry_count += 1

            if response:
                print_color(f"🤖 says: {response}", GREEN)
                if wait_for_window == "Minecraft":
                    try:
                        requests.post('http://localhost:3000/chat', json={'message': response})
                    except requests.exceptions.RequestException as e:
                        print(f"Failed to send message to Node.js server: {e}")
                
                tts_helper.speech(response)
            else:
                print("Chat call failed, retried 3 times")
            
            # After replying, continue screen recording
            recorder.start_recording()
