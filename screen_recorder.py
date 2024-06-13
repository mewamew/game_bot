import cv2
import numpy as np
import pyautogui
import time
import os
import pygetwindow as gw
import threading

class ScreenRecorder:
    def __init__(self, region=None):
        self.region = region
        self.screen_size = (region[2], region[3]) if region else pyautogui.size()
        self.fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.max_files = 300
        self.recording_thread = None
        self.record = []
        self.stop_record = False
    def list_all_windows(self):
        windows = gw.getAllWindows()
        for window in windows:
            print(f"Title: {window.title}, Size: ({window.width}, {window.height}), Position: ({window.left}, {window.top})")


    def wait_for_window(self, window_title):
        while True:
            window = gw.getWindowsWithTitle(window_title)
            if window and window[0]:
                self.region = (window[0].left, window[0].top, window[0].width, window[0].height)
                self.screen_size = (window[0].width, window[0].height)
                break
            else:
                time.sleep(1)

    def _start_recording(self):
        while not self.stop_record:
            img = pyautogui.screenshot(region=self.region)
            self.record.append(img)
            if len(self.record) > self.max_files:
                self.record.pop(0)
            time.sleep(0.1) 


    def start_recording(self):
        self.stop_record = False
        self.recording_thread = threading.Thread(target=self._start_recording)
        self.recording_thread.start()
        
    def fetch_record(self):
        output_filename="output.mp4"
        fps = 10
        
        if not self.record:
            print("No frames recorded.")
            return

        # 取最新的50帧
        frames_to_write = self.record[-50:]

        # 创建视频写入对象
        out = cv2.VideoWriter(output_filename, self.fourcc, fps, self.screen_size)

        for frame in frames_to_write:
            # 将PIL图像转换为OpenCV格式
            frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
            out.write(frame)

        out.release()
        return output_filename
        
        
    def stop_recording(self):
        self.stop_record = True
        if self.recording_thread:
            self.recording_thread.join()
            self.recording_thread = None


# 使用示例
if __name__ == "__main__":
    recorder = ScreenRecorder()
    recorder.list_all_windows()
