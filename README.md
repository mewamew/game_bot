# game_bot
**本项目只用于娱乐，没有实际用途**  
bot可以在你玩游戏的期间问答（吐槽）你的问题

## 环境要求 (System Requirements)
- **操作系统 (Operating System)**: Windows  
- **Python 版本 (Python Version)**: 3.10  
- **游戏版本 (Game Version)**: Minecraft 1.20.4
- **Node.js 环境 (Node.js Environment)**:
  - 安装 Node.js (Install Node.js): [官网链接 (Official Website)](https://nodejs.org/en)
  - 版本 (Version): node.js v20.14.0  
  - npm 版本 (npm Version): 10.7.0  
- **权限要求 (Permission Requirements)**: 需要麦克风权限 (Requires microphone access)

## 安装步骤 (Installation Steps)
1. 进入项目目录 (Enter the project directory):
   ```bash
   cd mc_bot
   ```
2. 安装pyton依赖 (Install Python dependencies):
   ```bash
   pip install -r requirements.txt
   ```

3. 安装node.js依赖 (Install Node.js dependencies):
   ```bash
   npm install
   ```


## 运行指南 (Running Guide)
### 设置 Gemini 的 API Key (Setting up Gemini's API Key)
- 在命令行中设置环境变量 (Set the environment variable in the command line):
  ```bash
  set GENAI_API_KEY=<YOUR_API_KEY>
  ```
- API KEY 可��在 [Google AI Studio](https://aistudio.google.com/) 生成 (API KEY can be generated at Google AI Studio).

### 启动程序 (Starting the Program)
1. 启动 Minecraft，开启局域网模式，设置端口为 28888 (Start Minecraft, enable LAN mode, set port to 28888).
2. 运行主程序 (Run the main program):
   ```bash
   python main.py
   ```

### 启动参数 (Startup Arguments)
- `--window`: 监听的窗口名称 (默认: "Minecraft") (Window name to listen to, default: "Minecraft")
- `--tts`: TTS 模式 (online 或 local) (默认: "local") (TTS mode, either "online" or "local", default: "local")
- `--list-windows`: 列出当前所有窗口 (List all current windows)

#### 如果选择 online 模式 (If choosing online mode)
- 使用字节火山引擎的API (Uses ByteDance Volcano Engine API)
- 需要设置以下环境变量 (Need to set the following environment variables):
  - `TTS_ACCESS_TOKEN`: 访问令牌 (Access token)
  - `TTS_CLUSTER`: 集群信息 (Cluster information)

示例 (Example):
```bash
python main.py --window "Minecraft" --tts "local"
```

### 功能说明 (Functionality Description)
- 程序启动后，会监听指定窗口的语音输入，并通过 TTS 服务进行语音合成。
- 如果监听的窗口是 Minecraft，会启动一个 Node.js 进程来处理游戏内的聊天功能。
- 录屏功能会在检测到语音输入时启动，并在语音输入结束后停止。
- 通过 Flask 提供的 API 接口与 Node.js 服务器进行通信。

### 注意事项 (Notes)
- 请确保在运行程序前，已正确配置和安装所有依赖项。
- 需要麦克风权限以进行语音检测和合成。