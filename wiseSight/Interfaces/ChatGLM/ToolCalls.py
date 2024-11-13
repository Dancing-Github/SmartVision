import json

toolFunctions = [
    {
        "name": "bus_num_detector",
        "description": "获取当前看到的公交车的号码，是多少路公交车",
        "parameters": {},
    },

    {
        "name": "ocr_direct",
        "description": "读取说明书、药物处方等文件的内容",
        "parameters": {},
    },

    {
        "name": "congestion_detector",
        "description": "获取道路的拥塞状况，车多 or 车少，人多 or 人少",
        "parameters": {},
    },
    {
        "name": "traffic_light_detection",
        "description": "获取红绿灯当前的颜色",
        "parameters": {},
    },
    {
        "name": "key_object_location_hint",
        "description": "获取某个物品的位置，帮助用户找东西，例如钱包、钥匙、手机、遥控器等，例如：钥匙在哪里？",
        "parameters": {
            "type": "object",
            "properties": {
                "thing": {
                    "type": "string",
                    "description": "所需要找的物品, e.g. 钱包 | 钥匙 | 手机 | 遥控器 ",
                },
            },
            "required": ["thing"],
        },

    },

    {
        "name": "get_current_weather",
        "description": "获取特定城市的天气信息，比如广州的天气",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "城市名称, e.g. 广州市番禺区",
                },
            },
            "required": ["location"],
        },
    },
    {
        "name": "get_surrounding",
        "description": "获取某个地点周边的信息，例如餐馆、酒店、银行、医院等",
        "parameters": {
            "type": "object",
            "properties": {
                "address": {
                    "type": "string",
                    "description": "某个特定的地点, e.g. 广州图书馆",
                },
                "keywords": {
                    "type": "string",
                    "description": "想要在周边寻找的兴趣点, 使用 '|' 隔开, e.g. 肯德基 | 麦当劳",
                }
            },
            "required": ["address", "keywords"],
        },
    },
    {
        "name": "walking_from_org_to_dst",
        "description": "获取从起点到终点的步行路线，并开始导航播报",
        "parameters": {
            "type": "object",
            "properties": {
                "origin": {
                    "type": "string",
                    "description": "起点地址, e.g. 华南理工大学大学城校区",
                },
                "destination": {
                    "type": "string",
                    "description": "终点地址, e.g. 中山大学大学城校区",
                },
            },
            "required": ["origin", "destination"],
        },
    },
    {
        "name": "transits_from_org_to_dst",
        "description": "获取从起点到终点的交通路线, 包括公交车和地铁",
        "parameters": {
            "type": "object",
            "properties": {
                "origin": {
                    "type": "string",
                    "description": "起点地址, e.g. 华南理工大学大学城校区",
                },
                "destination": {
                    "type": "string",
                    "description": "终点地址, e.g. 中山大学大学城校区",
                },
            },
            "required": ["origin", "destination"],
        },
    }
]

with open("./data/toolFunctions.json", "r",encoding="utf-8") as f:
    toolFunctions=json.load(f)
