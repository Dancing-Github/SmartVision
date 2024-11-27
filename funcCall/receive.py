import os
from flask import Flask, request
import logging, json

app = Flask(__name__)

# 定义日志文件路径
log_directory = './'
log_filename = 'mylog.log'
log_filepath = os.path.join(log_directory, log_filename)

# 定义日志级别
LOG_LEVEL = logging.DEBUG

# 配置日志
logging.basicConfig(filename=log_filepath, level=LOG_LEVEL)


@app.route('/uploadImage', methods=['POST'])
def uploadImage():
    print("uploadImage!")
    print(request.form, '---------------')
    print(request.files, '---------------')
    uploadFile = request.files["imageFile"]
    # return 'File uploaded successfully.'

    # 1、输出测试
    print("==============")
    print(uploadFile)

    # 记录相关信息
    app.logger.info('Received upload request')  # 可以根据需要添加更多的日志记录语句

    # 2、将上传的图片存储到硬盘
    uploadFile.save(uploadFile.filename)

    # 3、返回成功信息
    return "success"


@app.route('/uploadAudio', methods=['POST'])
def uploadAudio():
    print("uploadAudio!")
    print(request.form, '---------------')
    print(request.files, '---------------')
    uploadFile = request.files["audioFile"]
    # return 'File uploaded successfully.'

    # 1、输出测试
    print("==============")
    print(uploadFile)

    # 记录相关信息
    app.logger.info('Received upload request')  # 可以根据需要添加更多的日志记录语句

    # 2、将上传的图片存储到硬盘
    uploadFile.save(uploadFile.filename)

    # 3、返回成功信息
    return "success"


@app.route('/retriveText', methods=['GET'])
def rertriveText():
    dict = {"text": "测试测试"}
    text = json.dumps(dict)
    print("retriveText!")
    app.logger.info('Received request from {}'.format(request.remote_addr))
    return text


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=28080)
