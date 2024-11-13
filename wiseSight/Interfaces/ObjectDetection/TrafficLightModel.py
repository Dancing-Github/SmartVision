import os

# import tensorflow as tf

# This guide can only be run with the torch backend.
os.environ["KERAS_BACKEND"] = "torch"

# tf.config.set_soft_device_placement(True)
# physical_devices = tf.config.list_physical_devices('GPU')
# if len(physical_devices) > 0:
#     for pd in physical_devices:
#         tf.config.experimental.set_memory_growth(pd, True)

import numpy as np
from PIL import Image
from keras.models import load_model


class TrafficLightModel:
    def __init__(self, model_path='/home/cike/xyq/mmdetction/traffic_light_model.h5'):
        # with tf.device(tf_device):
        self.model = load_model(model_path)

    def inferFunction(self, image):
        # Load and preprocess the image
        input_image = self._load_and_preprocess_image(image)

        # Perform inference using the model
        output = self.model.predict(input_image)

        # Map the output to the corresponding color
        predicted_color = self._map_output_to_color(output)

        return predicted_color

    def _load_and_preprocess_image(self, image):
        # 加载图像并调整大小以匹配模型的输入大小
        img = Image.fromarray(np.uint8(image))
        img = img.resize((64, 64))  # 将大小更改为(64, 64)

        # 将图像转换为NumPy数组
        img_array = np.array(img)

        # 预处理图像（根据模型的要求可能需要进行调整）
        img_array = img_array / 255.0  # 归一化到[0, 1]
        img_array = np.expand_dims(img_array, axis=0)  # 添加批次维度

        return img_array

    def _map_output_to_color(self, output):
        # Map the model output to the corresponding color
        # You may need to customize this based on your model's output format
        if output[0][0] > output[0][1] and output[0][0] > output[0][2]:
            return "检测到交通灯为绿色"
        elif output[0][1] > output[0][0] and output[0][1] > output[0][2]:
            return "检测到交通灯为红色"
        else:
            return "检测到交通灯为黄色"


if __name__ == '__main__':
    # Load the traffic light image
    image_path = '/home/cike/xyq/mmdetction/yellow.jpg'
    image = Image.open(image_path)

    # Create an instance of the TrafficLightModel
    traffic_light_model = TrafficLightModel()
    print(traffic_light_model.model.summary())

    # Perform inference
    result = traffic_light_model.inferFunction(image)
    print(result)
