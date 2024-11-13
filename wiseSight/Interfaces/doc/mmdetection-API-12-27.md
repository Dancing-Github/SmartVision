## Code

```python
# project path: /home/cike/xyq/mmdetction
# environment: xyq
# server: /home/cike/xyq/mmdetction/xyq_server.py
# client_template:/home/cike/xyq/mmdetction/client_template.ipynb
```

# keyObject_LocationHint

## API Reference

**Location**:   `POST`  'http://localhost:5002/keyObject_LocationHint'

**Properties**:

| Field       | Required | Type   | Desc    | Example Value |
|-------------|----------|--------|---------|---------------|
| text_prompt | yes      | string | 需要寻找的物品 | ‘wallet'      |

**Returns**:

| Field  | Type     | Desc        | Example Value                                                                                                                                                                                                                                                                                                                       |
|--------|----------|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| result | string   | 用于输入语言模型的示例 | Output a paragraph describing the scene where the wallet is located and the positions of other objects inside the adjacent rooms relative to it.Scene: living_room.Coordinates of key is (137,127) Coordinates of objects around the key aretable(152,127) key(205,126) cellular_telephone(207,76) booklet(274,100) thread(286,181) |
| scene  | string   | 物体所在的地方     | bedrom                                                                                                                                                                                                                                                                                                                              |
| label  | string数组 | 物体周围的物品     | ['table', 'key', 'cellular_telephone', 'packet', 'thread']                                                                                                                                                                                                                                                                          |

#### 调用例子

```
from interface import mmdetectionInterface
model = mmdetectionInterface(device='cuda:2')

root_path="/home/cike/xyq/mmdetction/"
img_path=root_path+text_prompt+".jpg"
with open(img_path, 'rb') as f:
        image = f.read()
        
result = model.keyObject_LocationHint(input=image, text_object=text_prompt)
#返回示例
result
'''
Output a paragraph describing the scene where the {text_object} is located and the positions of other objects inside the adjacent rooms relative to it.Scene: {scene}.Coordinates of key is ({int(x0)},{int(y0)}) Coordinates of objects around the key are "{ object['label']}({object['center'][0]},{object['center'][1]}) "
'''
'''
Output a paragraph describing the scene where the wallet is located and the positions of other objects inside the adjacent rooms relative to it.Scene: living_room.Coordinates of key is (137,127) Coordinates of objects around the key aretable(152,127) key(205,126) cellular_telephone(207,76) booklet(274,100) thread(286,181)
'''

```

#  

# keyObjectDetector

## API Reference

**Location**:   `POST`  'http://localhost:5002/keyObjectDetector'

ps:用于检测是否有重要物体，如果有则保存图片

**Properties**:

| Field | Required | Type  | Desc    | Example Value                                   |
|-------|----------|-------|---------|-------------------------------------------------|
| image | yes      | bytes | 图片二进制形式 | with open(img_path, 'rb') as f:image = f.read() |

**Returns**:

| Field  | Type | Desc                   | Example Value |
|--------|------|------------------------|---------------|
| result | Bool | 描述是否保存了图片，如果保存了则返回True |               |

#### 调用例子

```
from interface import mmdetectionInterface
model = mmdetectionInterface(device='cuda:2')

root_path="/home/cike/xyq/mmdetction/"
img_path=root+"OIP-C.jpg"
with open(img_path, 'rb') as f:
        image = f.read()
        
result=model.keyObjectDetector(input=image)
#返回示例
#True 代表有图片被存入
```

# congestionDetector

## API Reference

**Location**:   `POST`  'http://localhost:5002/congestionDetector'

**Properties**:

| Field | Required | Type  | Desc    | Example Value                                   |
|-------|----------|-------|---------|-------------------------------------------------|
| image | yes      | bytes | 图片二进制形式 | with open(img_path, 'rb') as f:image = f.read() |

**Returns**:

| Field  | Type   | Desc   | Example Value |
|--------|--------|--------|---------------|
| result | string | 道路拥挤状况 | '马路上车辆较少'     |

#### 调用例子

```
from interface import mmdetectionInterface
model = mmdetectionInterface(device='cuda:2')

root_path="/home/cike/xyq/mmdetction/"
img_path=root+"00001.webp"
with open(img_path, 'rb') as f:
        image = f.read()
        
result=model.congestionDetector(input=image)
#返回示例
#'马路上车辆较少'
#'马路上堵塞严重'
```

# trafficLightDetector

## API Reference

**Location**:   `POST`  'http://localhost:5002/trafficLightDetector'

**Properties**:

| Field | Required | Type  | Desc    | Example Value                                   |
|-------|----------|-------|---------|-------------------------------------------------|
| image | yes      | bytes | 图片二进制形式 | with open(img_path, 'rb') as f:image = f.read() |

**Returns**:

| Field  | Type   | Desc  | Example Value |
|--------|--------|-------|---------------|
| result | string | 红绿灯颜色 | 'green'       |

#### 调用例子

```
from interface import mmdetectionInterface
model = mmdetectionInterface(device='cuda:2')

root_path="/home/cike/xyq/mmdetction/"
img_path=root+"00001.webp"
with open(img_path, 'rb') as f:
        image = f.read()
        
result=model.trafficLightDetector(input=image)
#返回示例
'green'
'red'
'yellow'
#'前方没有红绿灯' 前方没有红绿灯的话
```

# busDetector

## API Reference

**Location**:   `POST`  'http://localhost:5002/busDetector'

**Properties**:

| Field | Required | Type  | Desc    | Example Value                                   |
|-------|----------|-------|---------|-------------------------------------------------|
| image | yes      | bytes | 图片二进制形式 | with open(img_path, 'rb') as f:image = f.read() |

**Returns**:

| Field  | Type    | Desc                               | Example Value                                                                 |
|--------|---------|------------------------------------|-------------------------------------------------------------------------------|
| result | float数组 | 公交车所在位置（共四个数字，前两个为左上角坐标，后两个为右下角坐标） | [33.80661392211914, 44.0699348449707, 274.87481689453125, 190.92929077148438] |

#### 调用例子

```
from interface import mmdetectionInterface
model = mmdetectionInterface(device='cuda:2')

root_path="/home/cike/xyq/mmdetction/"
img_path=root+"bus.jpg"
with open(img_path, 'rb') as f:
        image = f.read()
        
result=model.busDetector(input=image)
#返回示例
#[33.80661392211914, 44.0699348449707, 274.87481689453125, 190.92929077148438]
#'前方无公交车' 如果没检测公交车的话
```

