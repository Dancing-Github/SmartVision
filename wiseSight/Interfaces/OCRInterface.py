# file_path:/home/cike/LJJ/paddleOCR/OCRInterface.py

import threading
from paddleocr import PaddleOCR

from Debug import logger


class OCRInterface(object):
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(OCRInterface, "_instance"):
            with OCRInterface._instance_lock:
                if not hasattr(OCRInterface, "_instance"):
                    # 类加括号就回去执行__new__方法，__new__方法会创建一个类实例
                    OCRInterface._instance = object.__new__(cls)  # 继承object类的__new__方法，类去调用方法，说明是函数，要手动传cls
        return OCRInterface._instance  # obj1
        # 类加括号就会先去执行__new__方法，再执行__init__方法

    def __init__(self):
        # Loading the PaddleOCR model
        # det_model_dir='{your_det_model_dir}', 默认为ch_PP-OCRv4_det_infer
        # cls_model_dir='{your_cls_model_dir}', 默认为ch_ppocr_mobile_v2.0_cls_infer
        # rec_rec_char_path='{your_rec_char_dict_path}',默认为ppocr_keys_v1.txt
        # rec_model_path='{your_rec_model_path}',默认为ch_PP-OCRv4_rec_infer
        self.paddleOCR = PaddleOCR(use_angle_cls=True, lang="ch", use_gpu=False)
        logger.info("Model-paddleOCR loaded successfully.")

    def inferFunction(self, input):
        print("OCRInterface inferFunction")
        result = self.paddleOCR.ocr(input, cls=True)
        # print(result)
        # result0 = result[0]  # 获取框数
        # txts = [line[1][0] for line in result0]  # 获取文本
        # multi_line_str = '\n'.join(txts)  # 将文本数组转为多行字符串
        # print(multi_line_str)
        return result
        # 对识别文本加以处理

    def ocr_direct(self, input):
        result = self.inferFunction(input)
        result0 = result[0]  # 获取框数
        txts = [line[1][0] for line in result0]  # 获取文本
        multi_line_str = '\n'.join(txts)  # 将文本数组转为多行字符串
        output_text = "文本的内容是：\n" + multi_line_str
        print(output_text)
        return output_text


if __name__ == "__main__":
    # 调用例子
    testModule = OCRInterface()
    # 打开图片文件并以二进制模式读取
    with open('/home/cike/LJJ/paddleOCR/test-images/paper/3.jpg', 'rb') as file:
        input = file.read()
    output = testModule.inferFunction(input)
    print(output)
