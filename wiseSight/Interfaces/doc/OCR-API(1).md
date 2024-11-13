# OCR-API

## API Reference

**Location**:   `POST`  http://localhost:3001/predict_paddleOCR

**Properties**:

| Field | Required | Type  | Desc    | Example Value    |
|-------|----------|-------|---------|------------------|
| data  | yes      | bytes | 二进制图片数据 | 以rb模式读取jpg文件所得的值 |

**Returns**:

| Field | Type   | Desc      | Example Value |
|-------|--------|-----------|---------------|
| text  | string | 图片转文字后的文本 | 帮我找一下药盒在哪里    |

## Code

```python
# project path: /home/cike/LJJ/paddleOCR
# environment: ljj-paddle-detection
# test demo: /home/cike/LJJ/paddleOCR/demo.py
```

### Server-OCRInterface.py

```python
# file_path:/home/cike/LJJ/paddleOCR/OCRInterface.py

from paddleocr import PaddleOCR
import logging
from flask import Flask, request, jsonify


class OCRInterface:
    def __init__(self):
        # Loading the PaddleOCR model
        # det_model_dir='{your_det_model_dir}', 默认为ch_PP-OCRv4_det_infer
        # cls_model_dir='{your_cls_model_dir}', 默认为ch_ppocr_mobile_v2.0_cls_infer
        # rec_rec_char_path='{your_rec_char_dict_path}',默认为ppocr_keys_v1.txt
        # rec_model_path='{your_rec_model_path}',默认为ch_PP-OCRv4_rec_infer
        self.ocr = PaddleOCR(use_angle_cls=True, lang="ch")
        logging.info("Model-paddleOCR loaded successfully.")

    def inferFunction(self, input):
        result = self.ocr.ocr(input, cls=True)
        result = result[0]  # 获取框数
        txts = [line[1][0] for line in result]  # 获取文本
        multi_line_str = '\n'.join(txts)  # 将文本数组转为多行字符串
        print(multi_line_str)
        return multi_line_str

    # 对识别文本加以处理
    def infertest(self, input):
        multi_line_str = self.inferFunction(input)
        output_text = "文本的内容是：\n" + multi_line_str
        print(output_text)
        return output_text

    # define the server parameters


server_path = '/predict_paddleOCR'
server_port = 3001

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Initialize Flask app 
app = Flask(__name__)

# Load the model
logging.info("Loading the paddleOCR model...")

testModule = OCRInterface()

logging.info("Model-paddleOCR loaded successfully.")


@app.route(server_path, methods=['POST'])
def predict():
    """Handle prediction requests."""
    logging.info("Received a prediction request.")

    # Process video and predict
    output = testModule.infertest(request.data)
    logging.info("Prediction completed. Sending response.")
    return output


if __name__ == "__main__":
    logging.info("Starting Flask server on port 3001...")
    app.run(debug=True, port=server_port)

    # # 调用例子
    # testModule=OCRInterface()
    # # 打开图片文件并以二进制模式读取
    # with open('/home/cike/LJJ/paddleOCR/test-images/paper/3.jpg', 'rb') as file:
    #     input = file.read()
    # output=testModule.infertest(input)
    # print(output)
```

### Client-test_server.py

```python
# file_path:/home/cike/LJJ/paddleOCR/test_server.py

import requests

# Flask服务器的URL
url = 'http://localhost:3001/predict_paddleOCR'

# 打开音频文件并以二进制模式读取
with open('/home/cike/LJJ/paddleOCR/test-images/paper/3.jpg', 'rb') as file:
    # 读取所有二进制数据
    input = file.read()

# 发送POST请求
response = requests.post(url, data=input)

# 打印响应
if response.status_code == 200:
    print("成功响应:", response.text)
else:
    print("请求失败，状态码:", response.status_code, "\n响应内容:", response.text)
```

## Model

### 模型安装

PaddleOCR（https://gitee.com/paddlepaddle/PaddleOCR/blob/release/2.6/doc/doc_ch/quickstart.md）

### 模型介绍

#### 模型链接

[PP-OCR系列模型列表](https://gitee.com/paddlepaddle/PaddleOCR/tree/release/2.6#%EF%B8%8F-pp-ocr%E7%B3%BB%E5%88%97%E6%A8%A1%E5%9E%8B%E5%88%97%E8%A1%A8%E6%9B%B4%E6%96%B0%E4%B8%AD)

#### 模型参数

```
ocr = PaddleOCR(use_angle_cls=True, lang="ch")

# det_model_dir='{your_det_model_dir}', 默认为ch_PP-OCRv4_det_infer
# cls_model_dir='{your_cls_model_dir}', 默认为ch_ppocr_mobile_v2.0_cls_infer
# rec_rec_char_path='{your_rec_char_dict_path}',默认为ppocr_keys_v1.txt
# rec_model_path='{your_rec_model_path}',默认为ch_PP-OCRv4_rec_infer
```

#### 输入图片格式

ndarray、 img_path 、 list 、 bytes

#### 调用例子

```
from paddleocr import PaddleOCR, draw_ocr
import os
ocr = PaddleOCR(use_angle_cls=True, lang="ch")  # need to run only once to download and load model into memory

with open('/home/cike/LJJ/Detection_of_Bus_Number_in_Bus_Panel-master/codes/thresh.jpg', 'rb') as file:
    input = file.read()
  
result = ocr.ocr(input, cls=True)
result = result[0]
txts = [line[1][0] for line in result]
multi_line_str = '\n'.join(txts)
print(multi_line_str)
```

