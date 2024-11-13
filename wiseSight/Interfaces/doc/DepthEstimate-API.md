## Code

```python
# Lap-Depth:project path: /home/cike/weiyuancheng/LapDepth-release
# environment: wyc_py_3.9
# server: /home/cike/weiyuancheng/LapDepth-release/DepthEstimation/server_copy.py
# call_template: /home/cike/weiyuancheng/LapDepth-release/DepthEstimation/DepthEInterface.py


# LangSam:project path: /home/cike/hds/langsam
# environment: sam
# server: /home/cike/hds/langsam/example_notebook/server_copy.py
# call_template: /home/cike/weiyuancheng/LapDepth-release/DepthEstimation/DepthEInterface.py

# the LangSam model is a helper model for Lap-Depth model, so you can just only call for the lap-depth model
```

# Lap-Depth (Depth Estimation)

## API Reference

**Location**:   `POST`  'http://localhost:5001/process'

**Properties**:

| Field                | Required | Type     | Desc                                                         | Example Value                        |
|----------------------|----------|----------|--------------------------------------------------------------|--------------------------------------|
| img                  | yes      | Variable | Array                                                        | img = Image.open('./cike/pic/a.jpg') |
| input_outputLocation | yes      | string   | The path of the output image.                                | ‘./cike/output_pic’                  |
| input_promt          | yes      | string   | Input prompt words (used to label objects in LangSam boxes). | "Trash_Can"                          |

<!--# img = Image.open(img_path); //such as : img = Image.open('./cike/pic/a.jpg');-->



**Returns**:

| Field           | Type   | Desc                          | Example Value       |
|-----------------|--------|-------------------------------|---------------------|
| output_location | string | The path of the output image. | ‘./cike/output_pic’ |

#### Example

```python
from PIL import Image, ImageFile, PngImagePlugin
from flask import Flask, request, jsonify
import os
import requests
import json


class  DepthEInterface :
    def __init__(self) -> None:
        pass
    
    def interFunction(input) :
        input_image = input[0]
        input_outputLocation = input[1]
        input_promt = input[2]

        json_data = {
            "img" : input_image,
            "input_outputLocation" : input_outputLocation,
            "input_promt" : input_promt,
        }
        
        server_url = 'http://localhost:5001/process'
        response = requests.post(server_url, json=json_data)
        if response.status_code ==200 :
            json_response = response.json()
            return json_response['output_location'] #现在返回的是处理后的图片（即有bbox+distance information）的文件路径 #后续可以改为返回一个bool变量和String，表示前方 是否 有 xx 障碍物
        else:
            print("** Failed to get response from server, status code:", response.status_code) 
            return -1



# example
if __name__ == "__main__" :
    testModule=DepthEInterface()
    #假设input为主控传过来的json,则需要把这个文件改成服务器端口模式；
    #即若 input = request.json 
    #则：
    #input_image = Image.open(input.get('img_path'))
    #input_textPromt = input.get('promt');
    #input_outputLocation= input.get('output_location')
    #input =[input_image,input_outputLocation,input_textPromt,];

    #若不走http，直接当做函数调用，传入一个list的input即可，list里的元素如上；
    output=testModule.inferFunction(input)


#调用的逻辑可以看 /home/cike/weiyuancheng/LapDepth-release/DepthEstimation/server_copy.py  
#以及：/home/cike/hds/langsam/example_notebook/server_copy.py
```
