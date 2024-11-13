# Speech-To-Text-API

## API Reference

**Location**:   `POST`  http://localhost:3000/predict_funasr

**Properties**:

| Field | Required | Type  | Desc    | Example Value    |
|-------|----------|-------|---------|------------------|
| data  | yes      | bytes | 二进制音频数据 | 以rb模式读取amr文件所得的值 |

**Returns**:

| Field | Type   | Desc      | Example Value |
|-------|--------|-----------|---------------|
| text  | string | 语音转文字后的文本 | 帮我找一下药盒在哪里    |

## Code

```python
# project path: /home/cike/LJJ/FunASR
# environment: ljj-funasr
# test demo: /home/cike/LJJ/FunASR/UniASR-CT.ipynb
```

### Server-FunASRInterface.py

```python
# file_path:/home/cike/LJJ/FunASR/FunASRInterface.py

from flask import Flask, request, jsonify
import logging
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks


class FunASRInterface:
    def __init__(self):
        # Loading the UniASR model
        self.inference_16k_pipline = pipeline(
            task=Tasks.auto_speech_recognition,
            model='damo/speech_UniASR_asr_2pass-zh-cn-16k-common-vocab8358-tensorflow1-offline')
        logging.info("Model-UniASR loaded successfully.")

        # Load the punc_ct model
        self.inference_pipline = pipeline(
            task=Tasks.punctuation,
            model='damo/punc_ct-transformer_zh-cn-common-vocab272727-pytorch',
            model_revision="v1.1.7")
        logging.info("Model-punc_ct loaded successfully.")

    def inferFunction(self, input):
        rec_result = self.inference_16k_pipline(input)
        result = self.inference_pipline(text_in=rec_result['text'])
        return result['text']


# define the server parameters
server_path = '/predict_funasr'
server_port = 3000

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Initialize Flask app 
app = Flask(__name__)

# Load the model
logging.info("Loading the FunASR model...")
testModule = FunASRInterface()
logging.info("The FunASR model loaded successfully!")


@app.route(server_path, methods=['POST'])
def predict():
    """Handle prediction requests."""
    logging.info("Received a prediction request.")
    output = testModule.inferFunction(request.data)
    logging.info("Prediction completed. Sending response.")
    return output


# example
if __name__ == "__main__":
    logging.info("Starting Flask server on port 3000...")
    app.run(debug=True, port=server_port)

    # # 调用例子
    # testModule=FunASRInterface()
    # # 打开音频文件并以二进制模式读取
    # with open('/home/cike/LJJ/FunASR/test-wav/FinalAudio.amr', 'rb') as file:
    #     input = file.read()
    # output=testModule.inferFunction(input)
```

### Client-test_server.ipynb

```python
# file_path:/home/cike/LJJ/FunASR/test_server.ipynb
import requests

# Flask服务器的URL
url = 'http://localhost:3000/predict_funasr'

# 打开音频文件并以二进制模式读取
with open('/home/cike/LJJ/FunASR/test-wav/FinalAudio.amr', 'rb') as file:
    # 读取所有二进制数据
    speech = file.read()

# 发送POST请求
response = requests.post(url, data=speech)

# 打印响应
if response.status_code == 200:
    print("成功响应:", response.text)
else:
    print("请求失败，状态码:", response.status_code, "\n响应内容:", response.text)
```

## Model

### 模型安装

FunASR（https://alibaba-damo-academy.github.io/FunASR/en/installation/installation.html）

### 模型介绍

#### 语音识别

##### 模型链接

[UniASR语音识别-中文-通用-16k-离线](https://www.modelscope.cn/models/damo/speech_UniASR_asr_2pass-zh-cn-16k-common-vocab8358-tensorflow1-offline/summary)

##### 输入音频格式

输入音频支持wav与pcm格式音频，以wav格式输入为例，支持以下几种输入方式：

- wav文件路径，例如：data/test/audios/asr_example.wav
- wav二进制数据，格式bytes，例如：用户直接从文件里读出bytes数据或者是麦克风录出bytes数据
- wav文件url，例如：https://isv-data.oss-cn-hangzhou.aliyuncs.com/ics/MaaS/ASR/test_audio/asr_example.wav

##### 调用例子

```
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

inference_16k_pipline = pipeline(
    task=Tasks.auto_speech_recognition,
    model='damo/speech_UniASR_asr_2pass-zh-cn-16k-common-vocab8358-tensorflow1-offline')

rec_result = inference_16k_pipline(audio_in='https://modelscope.oss-cn-beijing.aliyuncs.com/test/audios/asr_example.wav')
print(rec_result)
```

#### 标点恢复

##### 模型链接

[CT-Transformer标点-中文-通用-pytorch](https://modelscope.cn/models/damo/punc_ct-transformer_zh-cn-common-vocab272727-pytorch/summary)

##### 调用例子

```
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

inference_pipline = pipeline(
    task=Tasks.punctuation,
    model='damo/punc_ct-transformer_zh-cn-common-vocab272727-pytorch',
    model_revision="v1.1.7")

rec_result = inference_pipline(text_in='example/punc_example.txt')
print(rec_result)
```

