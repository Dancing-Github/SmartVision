"""
This script is designed to mimic the OpenAI API interface to interact with the cogvlm-17B
It demonstrates the integration of image and text-based inputs for generating responses.
Currently, this model can only process a single image.
So do not use this script to process multiple images in one conversation.(Including the image in the history)
And it is only for chat model, not base model.
"""

# 先运行下面的命令启动服务器
# MODEL_PATH=/home/cike/glm_and_vlm/cogvlm-chat python openai_api.py

import requests
import json
import base64

base_url = "http://127.0.0.1:8000"


def create_chat_completion(model, messages, temperature=0.8, max_tokens=2048, top_p=0.8, use_stream=False):
    data = {
        "model": model,
        "messages": messages,
        "stream": use_stream,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
    }

    response = requests.post(f"{base_url}/v1/chat/completions", json=data, stream=use_stream)
    if response.status_code == 200:
        if use_stream:
            # 处理流式响应
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')[6:]
                    try:
                        response_json = json.loads(decoded_line)
                        content = response_json.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        print(content, end="")
                    except:
                        print()
                        print("Special Token:", decoded_line)
        else:
            # 处理非流式响应
            decoded_line = response.json()
            content = decoded_line.get("choices", [{}])[0].get("message", "").get("content", "")
            print(content)
    else:
        print("Error:", response.status_code)
        return None


def encode_image(image_path):
    """Getting the base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def simple_image_chat(use_stream=True, img_path=None):
    img_url = f"data:image/jpeg;base64,{encode_image(img_path)}"
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text", "text": "中文模式\n描述这张图片",
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": img_url
                    },
                },
            ],
        },

        # ... 接下来这段是 assistant 的回复和用户的回复。

        {
            "role": "assistant",
            "content": "The image displays information about the TV series 'Pantheon Season 2 (2023)'. It features the series title, a rating of 9.2, and a review snippet. The series is about a world where gods, humans, and mythical creatures coexist. The show aired in 2023 and has a duration of 16 episodes. The image also shows the series' release date, its rating on the Chinese TV website Douyin, and a rating percentage from another platform.",
        },
        {
            "role": "user",
            "content": "请用中文回答"
        },

        # 很抱歉, 我 cannot reply in Chinese. However, I can help with any other queries.
    ]
    create_chat_completion("cogvlm-chat-17b", messages=messages, use_stream=use_stream)


if __name__ == "__main__":
    simple_image_chat(use_stream=False, img_path="./test_img.png")
