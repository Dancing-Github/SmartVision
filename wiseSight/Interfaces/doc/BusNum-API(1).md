# BusNum-API

## API Reference

**Location**:   `POST`  http://localhost:3002/predict_busnum

**Properties**:

| Field | Required | Type  | Desc    | Example Value    |
|-------|----------|-------|---------|------------------|
| data  | yes      | bytes | 二进制图片数据 | 以rb模式读取jpg文件所得的值 |

**Returns**:

| Field | Type   | Desc      | Example Value |
|-------|--------|-----------|---------------|
| text  | string | 图片转文字后的文本 | 74            |

## Code

```python
# project path: /home/cike/LJJ/Detection_of_Bus_Number_in_Bus_Panel-master
# environment: ljj-busnum
# test demo: /home/cike/LJJ/Detection_of_Bus_Number_in_Bus_Panel-master/codes/03_OCR_Pipeline.ipynb
```

### Server-BusNumInterface.py

```python
# file_path:/home/cike/LJJ/Detection_of_Bus_Number_in_Bus_Panel-master/codes/BusNumInterface.py

from paddleocr import PaddleOCR
import logging
import torch
import numpy as np
import cv2
import os
import io
from PIL import Image
from flask import Flask, request, jsonify

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


class BusNumInterface:
    def __init__(self):
        # Loading the yolov5 model
        self.model = torch.hub.load('/home/cike/LJJ/Detection_of_Bus_Number_in_Bus_Panel-master/codes/yolov5', 'custom',
                                    path='best', source='local')
        logging.info("Model-yolov5 loaded successfully.")

        # Loading the PaddleOCR model
        # det_model_dir='{your_det_model_dir}', 默认为ch_PP-OCRv4_det_infer
        # cls_model_dir='{your_cls_model_dir}', 默认为ch_ppocr_mobile_v2.0_cls_infer
        # rec_rec_char_path='{your_rec_char_dict_path}',默认为ppocr_keys_v1.txt
        # rec_model_path='{your_rec_model_path}',默认为ch_PP-OCRv4_rec_infer
        self.ocr = PaddleOCR(use_angle_cls=True, lang="ch")
        logging.info("Model-paddleOCR loaded successfully.")

    # define helper functions to preprocess the ROI        
    def get_roi(self, img):
        # inference
        results = self.model(img)

        # img predictions (pandas)
        bounding_box = results.pandas().xyxy[0]

        # xmin
        x_min = int(bounding_box['xmin'][0])

        # xmax
        x_max = int(bounding_box['xmax'][0])

        # ymin
        y_min = int(bounding_box['ymin'][0])

        # ymax
        y_max = int(bounding_box['ymax'][0])

        # use numpy slicing to crop the region of interest
        roi = img[y_min:y_max, x_min:x_max]

        return roi

        # get grayscale image

    def get_grayscale(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return gray

    # thresholding
    def thresholding(self, image):
        thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        return thresh

    def inferFunction(self, input):
        # 使用io.BytesIO()创建字节流对象
        byte_stream = io.BytesIO(input)
        # 使用Image.open()加载字节流并解码为图像
        image = Image.open(byte_stream)
        # convert to numpy array
        img = np.array(image)
        # 图像处理
        roi = self.get_roi(img)
        gray = self.get_grayscale(roi)
        thresh = self.thresholding(gray)

        # 文本识别
        # args-img: img for OCR, support ndarray, img_path and list or ndarray
        result = self.ocr.ocr(thresh, cls=True)
        result = result[0]  # 获取框数
        txts = [line[1][0] for line in result]  # 获取文本
        multi_line_str = '\n'.join(txts)  # 将文本数组转为多行字符串
        return multi_line_str

    # 对识别内容加以处理
    def infertest(self, input):
        multi_line_str = self.inferFunction(input)
        output_text = "前方公交车数字车牌是：\n" + multi_line_str
        print(output_text)
        return output_text

    # define the server parameters


server_path = '/predict_busnum'
server_port = 3002

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Initialize Flask app 
app = Flask(__name__)

# Load the model
logging.info("Loading the busnum model...")

testModule = BusNumInterface()

logging.info("Model-busnum loaded successfully.")


@app.route(server_path, methods=['POST'])
def predict():
    """Handle prediction requests."""
    logging.info("Received a prediction request.")

    # Process video and predict
    output = testModule.infertest(request.data)
    logging.info("Prediction completed. Sending response.")
    return output


if __name__ == "__main__":
    logging.info("Starting Flask server on port 3002...")
    app.run(debug=True, port=server_port)
    # # 调用例子
    # testModule=BusNumInterface()
    # # 读取文件
    # with open('/home/cike/LJJ/Detection_of_Bus_Number_in_Bus_Panel-master/data/test/images/bus_video1_425.jpg', 'rb') as file:
    #     input = file.read()
    # output=testModule.infertest(input)
    # print(output)
```

### Client-test_server.ipynb

```python
# file_path:/home/cike/LJJ/FunASR/test_server.ipynb
import requests
from PIL import Image

# Flask服务器的URL
url = 'http://localhost:3002/predict_busnum'

with open('/home/cike/LJJ/Detection_of_Bus_Number_in_Bus_Panel-master/data/test/images/bus_video1_425.jpg',
          'rb') as file:
    # 读取所有二进制数据
    input = file.read()
# opening the File
# img = Image.open('/home/cike/LJJ/Detection_of_Bus_Number_in_Bus_Panel-master/data/test/images/bus_video1_425.jpg')
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

yolov5（https://github.com/crushedmonster/Detection_of_Bus_Number_in_Bus_Panel/blob/master/codes/03_OCR_Pipeline.ipynb）

PaddleOCR（https://gitee.com/paddlepaddle/PaddleOCR/blob/release/2.6/doc/doc_ch/quickstart.md）

### 模型介绍

#### 图像处理——截取公交车数字板

##### 模型链接

[Detection_of_Bus_Number_in_Bus_Panel](https://github.com/crushedmonster/Detection_of_Bus_Number_in_Bus_Panel/tree/master)

##### 调用例子

```
# OCR Pipeline Overview
In this section, we will be implementing the full pipeline by making use of the custom object detector trained (using YOLOv5) and Optical Character Recognition (OCR), to extract bus number from bus panel and convert the extracted text to audio.
## Setup
All libraries used should be added here.

# import libraries
import torch
import numpy as np
import cv2
import imutils
from PIL import Image
import pytesseract
from gtts import gTTS
import IPython.display as ipd
import matplotlib.pyplot as plt
%matplotlib inline
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"


# select a test image
test_image = '/home/cike/LJJ/Detection_of_Bus_Number_in_Bus_Panel-master/data/test/images/bus_video1_425.jpg'

# opening the File
img = Image.open(test_image)
# convert to numpy array
img = np.array(img)
plt.imshow(img)
# model
model = torch.hub.load('yolov5', 'custom', path='best', source='local') 

# inference
results = model(img)

# results
results.print()  # or .show(), .save(), .crop(), .pandas(), etc.
bounding_box = results.pandas().xyxy[0]  # img predictions (pandas)
display(bounding_box)

### Create Region of Interest (ROI)
# xmin
x_min = int(bounding_box['xmin'][0])

# xmax
x_max = int(bounding_box['xmax'][0])

# ymin
y_min = int(bounding_box['ymin'][0])

# ymax
y_max = int(bounding_box['ymax'][0])

# use numpy slicing to crop the region of interest
roi = img[y_min:y_max,x_min:x_max] 
# plot the region of interest
plt.imshow(roi)

### Preprocess
# define a helper function to show image
def show_pic(img):
    fig = plt.figure(figsize=(15,15))
    ax = fig.add_subplot(111)
    ax.imshow(img,cmap='gray')
    
    
# define helper functions to preprocess the ROI
# get grayscale image
def get_grayscale(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray

# thresholding
def thresholding(image):
    thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return thresh

gray = get_grayscale(roi)
thresh = thresholding(gray)
show_pic(gray)
show_pic(thresh)
```

#### 文本识别——识别截取后的图片文字

##### 模型链接

[PP-OCR系列模型列表](https://gitee.com/paddlepaddle/PaddleOCR/tree/release/2.6#%EF%B8%8F-pp-ocr%E7%B3%BB%E5%88%97%E6%A8%A1%E5%9E%8B%E5%88%97%E8%A1%A8%E6%9B%B4%E6%96%B0%E4%B8%AD)

##### 调用例子

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

