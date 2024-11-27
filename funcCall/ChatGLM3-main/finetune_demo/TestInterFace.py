import os

os.environ["CUDA_VISIBLE_DEVICES"] = "7"

from tqdm import tqdm
from ChatGLM import toolFunctions, logger
from combine_data import analysis_data
import jsonlines
from pathlib import Path
from time import time


def test_data(file: Path, interface=None):
    type_count = {}
    for type in ["get_current_weather", "traffic_light_detection", "bus_num_detector",
                 "congestion_detector", "get_surrounding", "walking_from_org_to_dst",
                 "transits_from_org_to_dst", "N/A"]:
        type_count.update({type: {"GT": 0, "TP": 0, "FP": 0, "FN": 0}})
    with jsonlines.open(file, 'r') as fr:
        data = list(fr)
    logger.debug(f"{file}  {len(data)}")

    for item in tqdm(data):
        conversations = item['conversations']
        pure_conv = True
        for idx, turn in enumerate(conversations):
            if turn['role'] != 'tool':
                continue
            pure_conv = False
            gt_type = turn['name']
            messages = conversations[:idx - 1]
            break
        if pure_conv:
            gt_type = 'N/A'
            messages = conversations[:-1]
        type_count[gt_type]["GT"] += 1

        if interface is None:
            continue

        pred_type = testChatInterface(messages, interface)
        if pred_type != gt_type:
            type_count[gt_type]["FN"] += 1
            if pred_type in type_count:
                type_count[pred_type]["FP"] += 1
        else:
            type_count[gt_type]["TP"] += 1

    if interface is None:
        logger.debug(type_count)
    else:
        sum_GT = sum([v["GT"] for v in type_count.values()])
        # micro
        sum_TP = sum([v["TP"] for v in type_count.values()])
        sum_FP = sum([v["FP"] for v in type_count.values()])
        sum_FN = sum([v["FN"] for v in type_count.values()])
        all_success = sum_TP / sum_GT
        mic_precision = sum_TP / (sum_TP + sum_FP) if sum_TP + sum_FP > 0 else 0
        mic_recall = sum_TP / (sum_TP + sum_FN) if sum_TP + sum_FN > 0 else 0
        micro_f1 = 2 * mic_precision * mic_recall / (
                mic_precision + mic_recall) if mic_precision + mic_recall > 0 else 0
        logger.debug(f"All success rate:{all_success}. Micro(p, r, f1): ({mic_precision}, {mic_recall}, {micro_f1})")

        for type in type_count:
            GT = type_count[type]["GT"]
            # macro
            TP = type_count[type]["TP"]
            FP = type_count[type]["FP"]
            FN = type_count[type]["FN"]
            success = TP / GT
            precision = TP / (TP + FP) if TP + FP > 0 else 0
            recall = TP / (TP + FN) if TP + FN > 0 else 0
            f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0
            type_count[type].update({"success": success, "precision": precision, "recall": recall, "f1": f1})
        logger.debug(type_count)

        avg_success = sum([v["success"] for v in type_count.values()]) / len(type_count)
        mac_precision = sum([v["precision"] for v in type_count.values()]) / len(type_count)
        mac_recall = sum([v["recall"] for v in type_count.values()]) / len(type_count)
        macro_f1 = sum([v["f1"] for v in type_count.values()]) / len(type_count)
        logger.debug(f"Avg success rate:{avg_success}. Macro(p, r, f1): ({mac_precision}, {mac_recall}, {macro_f1})")


def testChatInterface(messages, interface):
    use_stream = False

    input = {
        "functions": toolFunctions,  # 函数定义
        "model": "chatglm3-6b",  # 模型名称
        "messages": messages,  # 会话历史
        "stream": use_stream,  # 是否流式响应
        "max_tokens": 500,  # 最多生成字数
        "temperature": 0.0,  # 温度
        "top_p": 0.8,  # 采样概率
    }

    start = time()
    output = interface.inferFunction(input)
    end = time()
    print('time used: ', end - start)
    # print(output)
    choice = output.model_dump().get("choices", [{}])[0]
    msg = choice.get("message", {})

    finish_reason = choice.get("finish_reason", None)

    if finish_reason == 'tool_calls':
        function_name = msg["tool_calls"][0]["function"]["name"].strip()
        function_arg = msg["tool_calls"][0]["function"]["arguments"]
    elif finish_reason == 'function_call':
        function_name = msg["function_call"]["name"].strip()
        function_arg = msg["function_call"]["arguments"]
    else:
        function_name = 'N/A'
    return function_name


if __name__ == "__main__":
    analysis_data(Path('data/fix'))
    WITCH_TO_USE = 0

    if WITCH_TO_USE == 1:
        from ChatGLMInterface import ChatGLMInterface

        model = ChatGLMInterface(device="cuda:0")

    elif WITCH_TO_USE == 0:
        from ChatGPTInterface import ChatGPTInterface

        model = ChatGPTInterface()
        messages = [
            {
                "role": "system",
                "content": "你是AI智能眼镜，帮助视障群体的住行。请根据需要调用所给的工具函数，仔细回答用户的提问。"
            },
            {
                "role": "user",
                "content": "请问对于视障人体出行有什么建议？"
            }

        ]
        testChatInterface(messages, model)
        exit(WITCH_TO_USE)

    elif WITCH_TO_USE == -1:
        model = None

    else:
        raise ValueError(f"wrong WITCH_TO_USE {WITCH_TO_USE}")

    test_data(Path('data/fix/test.jsonl'), model)
