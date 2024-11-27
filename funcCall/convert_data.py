import json

role_dict = {
    "usr": "user",
    "sys": "assistant"
}


def extract_conversation(messages: list) -> list:
    conversation = [{
        "role": role_dict[msg["role"]],
        "content": msg["content"],
    } for msg in messages]
    return conversation


def read_data(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def convert_format(path: str) -> list:
    data = read_data(path)
    conversations = []
    for one in data.values():
        conversations.append({
            "conversations": extract_conversation(one["messages"])
        })
    return conversations


if __name__ == "__main__":
    train = convert_format("./CrossWOZ_train.json")
    with open("./ChatGLM3-main/finetune_demo/data/raw/train.json", "w", encoding="utf-8") as f:
        json.dump(train, f, ensure_ascii=False, indent=4)
        print(len(train), train[0])
    val = convert_format("./CrossWOZ_val.json")
    with open("./ChatGLM3-main/finetune_demo/data/raw/val.json", "w", encoding="utf-8") as f:
        json.dump(val, f, ensure_ascii=False, indent=4)
        print(len(val), val[0])
    test = convert_format("./CrossWOZ_test.json")
    with open("./ChatGLM3-main/finetune_demo/data/raw/test.json", "w", encoding="utf-8") as f:
        json.dump(test, f, ensure_ascii=False, indent=4)
    print(len(test), test[0])
