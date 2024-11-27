import json
import random
import jsonlines
from pathlib import Path

print(Path.cwd())


def combine_data(data_dir: Path, save_dir: Path):
    data_files = data_dir.rglob('*.json')
    data = []
    for file in data_files:
        with open(file, 'r', encoding='utf-8') as fr:
            data.extend(json.load(fr))
    random.shuffle(data)
    ratio = 0.1
    print(f"共{len(data)}, val{len(data) * ratio}, test{len(data) * ratio}, train{len(data) * (1 - ratio * 2)}")

    # delete old jsonl
    for file in save_dir.rglob('*.jsonl'):
        file.unlink()
    # create new jsonl
    for idx in range(len(data)):
        if idx < len(data) * ratio:
            with jsonlines.open(save_dir / 'val.jsonl', 'a') as fw:
                fw.write(data[idx])
        elif idx < len(data) * ratio * 2:
            with jsonlines.open(save_dir / 'test.jsonl', 'a') as fw:
                fw.write(data[idx])
        else:
            with jsonlines.open(save_dir / 'train.jsonl', 'a') as fw:
                fw.write(data[idx])


def analysis_data(save_dir: Path):
    saved_files = save_dir.rglob('*.jsonl')
    for file in saved_files:
        type_count = {
            "get_current_weather": 0,
            "traffic_light_detection": 0,
            "bus_num_detector": 0,
            "congestion_detector": 0,
            "get_surrounding": 0,
            "walking_from_org_to_dst": 0,
            "transits_from_org_to_dst": 0,
            "N/A": 0
        }
        with jsonlines.open(file, 'r') as fr:
            data = list(fr)
        print(file, len(data))
        for item in data:
            conversations = item['conversations']
            pure_conv = True
            for turn in conversations:
                if turn['role'] != 'tool':
                    continue
                pure_conv = False
                type_count[turn['name']] += 1
                break
            if pure_conv:
                type_count['N/A'] += 1
        print(file, type_count)


if __name__ == '__main__':
    # combine_data(Path('./data/raw'), Path('./data/fix'))
    analysis_data(Path('./data/fix'))
