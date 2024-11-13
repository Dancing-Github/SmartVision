import os

os.environ["CUDA_VISIBLE_DEVICES"] = "1,2,3"

import torch.multiprocessing as mp

mp.set_start_method('spawn', force=True)

from contextlib import asynccontextmanager
import torch
import uvicorn
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware

from Cores import Controller
from Debug import logger  # 请根据实际情况调整导入路径


@asynccontextmanager
async def lifespan(app: FastAPI):  # collects GPU memory
    yield
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post('/uploadImage')  # 安卓上传图片
async def upload_image(imageFile: UploadFile = File(...)):
    # print("uploadImage!")
    # 记录相关信息
    # logger.info('Received upload_image request')

    image = imageFile.file.read()
    controller.onUploadImage(image)
    # 将上传的图片存储到硬盘
    # with open(imageFile.filename, "wb") as f:
    #     f.write(image)
    # 返回成功信息
    return {"message": "success"}


@app.post('/uploadAudio')  # 安卓上传音频
async def upload_audio(audioFile: UploadFile = File(...)):
    # print("uploadAudio!")

    audio = audioFile.file.read()
    controller.onUploadAudio(audio)
    # 记录相关信息
    # logger.info('Received uploadAudio request')

    # 将上传的音频存储到硬盘
    with open(audioFile.filename, "wb") as f:
        f.write(audio)
    # 返回成功信息
    return {"message": "success"}


@app.get('/retrieveText')  # 安卓获取文本
async def retrieve_text(request: Request = None):
    # 记录相关信息
    # logger.info('Received retrieve_text from {}'.format(request.client.host))
    try:
        location_lat_lng = (request.headers['LAT'], request.headers['LNG'])
        logger.info(f"Location: {location_lat_lng}")
    except:
        location_lat_lng = None
    text = controller.onRetrieveText(location_lat_lng)
    # print("retrieveText!")
    return text


@app.get('/uploadText')  # debug 文本
async def upload_text(request: Request = None):
    # 记录相关信息
    # logger.info('Received retrieve_text from {}'.format(request.client.host))
    text = request.query_params["text"]
    controller.onUploadText(text)
    # print("uploadText!")
    return {"message": "success"}


if __name__ == '__main__':
    controller = Controller()
    uvicorn.run(app, host='0.0.0.0', port=28080)

# ssh -p 2028 -L 0.0.0.0:28080:127.0.0.1:28080 cike@202.38.247.79
#  export LD_LIBRARY_PATH=/home/cike/miniconda3/envs/apiLLM/lib:$PATH
#  export LD_LIBRARY_PATH=/home/cike/miniconda3/envs/wiseSight/lib:$PATH
#  export LD_LIBRARY_PATH=/home/cike/miniconda3/envs/cxfz/lib:$PATH
#  conda env config vars set LD_LIBRARY_PATH=...
