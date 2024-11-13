import io
import threading

import cv2
import numpy as np
import torch
from PIL import Image

from Debug import logger
from Interfaces.OCRInterface import OCRInterface


# os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


class BusNumInterface(object):
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(BusNumInterface, "_instance"):
            with BusNumInterface._instance_lock:
                if not hasattr(BusNumInterface, "_instance"):
                    # 类加括号就回去执行__new__方法，__new__方法会创建一个类实例
                    BusNumInterface._instance = object.__new__(cls)  # 继承object类的__new__方法，类去调用方法，说明是函数，要手动传cls
        return BusNumInterface._instance  # obj1
        # 类加括号就会先去执行__new__方法，再执行__init__方法

    def __init__(self, device="cuda:0"):
        # Loading the yolov5 model
        self.model = torch.hub.load('/home/cike/LJJ/Detection_of_Bus_Number_in_Bus_Panel-master/codes/yolov5', 'custom',
                                    path='best', source='local', device=device)
        logger.info("Model-yolov5 loaded successfully.")

        # Loading the PaddleOCR model
        # det_model_dir='{your_det_model_dir}', 默认为ch_PP-OCRv4_det_infer
        # cls_model_dir='{your_cls_model_dir}', 默认为ch_ppocr_mobile_v2.0_cls_infer
        # rec_rec_char_path='{your_rec_char_dict_path}',默认为ppocr_keys_v1.txt
        # rec_model_path='{your_rec_model_path}',默认为ch_PP-OCRv4_rec_infer
        self.ocr = OCRInterface()
        logger.info("Model-paddleOCR loaded successfully.")

    # define helper functions to preprocess the ROI
    def _get_roi(self, img):
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

    def _get_grayscale(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return gray

    # thresholding
    def _thresholding(self, image):
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
        roi = self._get_roi(img)
        gray = self._get_grayscale(roi)
        thresh = self._thresholding(gray)

        # 文本识别
        # args-img: img for OCR, support ndarray, img_path and list or ndarray
        result = self.ocr.inferFunction(thresh)
        # print(result)
        # result0 = result[0]  # 获取框数
        # txts = [line[1][0] for line in result0]  # 获取文本
        # multi_line_str = '\n'.join(txts)  # 将文本数组转为多行字符串
        # print(multi_line_str)
        return result

    # 对识别内容加以处理
    def busNum_detector(self, input):
        result = self.inferFunction(input)
        result0 = result[0]  # 获取框数
        txts = [line[1][0] for line in result0]  # 获取文本
        multi_line_str = '\n'.join(txts)  # 将文本数组转为多行字符串
        output_text = "前方公交车数字车牌是：\n" + multi_line_str
        print(output_text)
        return output_text


if __name__ == "__main__":
    # 调用例子
    testModule = BusNumInterface()
    # 读取文件
    with open('/home/cike/LJJ/Detection_of_Bus_Number_in_Bus_Panel-master/data/test/images/bus_video1_425.jpg',
              'rb') as file:
        input = file.read()
    output = testModule.inferFunction(input)
    print(output)
