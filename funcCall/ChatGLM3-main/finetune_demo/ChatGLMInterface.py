import threading
from pathlib import Path
from typing import Union

import torch
from peft import AutoPeftModelForCausalLM, PeftModelForCausalLM
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizer,
    PreTrainedTokenizerFast,
)
from ChatGLM import ChatCompletionRequest, create_chat_completion

ModelType = Union[PreTrainedModel, PeftModelForCausalLM]
TokenizerType = Union[PreTrainedTokenizer, PreTrainedTokenizerFast]

def _resolve_path(path: Union[str, Path]) -> Path:
    return Path(path).expanduser().resolve()

def load_model_and_tokenizer(model_dir: Union[str, Path], device) -> tuple[ModelType, TokenizerType]:
    model_dir = _resolve_path(model_dir)
    if (model_dir / 'adapter_config.json').exists():
        model = AutoPeftModelForCausalLM.from_pretrained(
            model_dir, trust_remote_code=True, device = device
        )
        tokenizer_dir = model.peft_config['default'].base_model_name_or_path
    else:
        model = AutoModelForCausalLM.from_pretrained(
            model_dir, trust_remote_code=True, device = device
        )
        tokenizer_dir = model_dir
    tokenizer = AutoTokenizer.from_pretrained(
        tokenizer_dir, trust_remote_code=True
    )
    return model, tokenizer

class ChatGLMInterface(object):
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(ChatGLMInterface, "_instance"):
            with ChatGLMInterface._instance_lock:
                if not hasattr(ChatGLMInterface, "_instance"):
                    # 类加括号就回去执行__new__方法，__new__方法会创建一个类实例
                    ChatGLMInterface._instance = object.__new__(cls)  # 继承object类的__new__方法，类去调用方法，说明是函数，要手动传cls
        return ChatGLMInterface._instance  # obj1
        # 类加括号就会先去执行__new__方法，再执行__init__方法

    def __init__(self, device="cuda:0"):

        self.device = device
        # self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

        # self.model_path = '/home/cike/glm_and_vlm/chatglm3-6b' # 下面加载的lora权重会设置base_model为此路径
        self.model_path = '/home/cike/HJS/funcCall/ChatGLM3-main/finetune_demo/output/checkpoint-3225'
        self.tokenizer_path = self.model_path

        # self.glmTokenizer = AutoTokenizer.from_pretrained(self.tokenizer_path, trust_remote_code=True)
        # if 'cuda' in self.device:  # AMD, NVIDIA GPU can use Half Precision
        #     self.glmModel = AutoModel.from_pretrained(self.model_path, trust_remote_code=True).to(self.device).eval()
        #     self.glmModel = torch.compile(self.glmModel)
        # else:  # CPU, Intel GPU and other GPU can use Float16 Precision Only
        #     self.glmModel = AutoModel.from_pretrained(self.model_path, trust_remote_code=True).float().to(
        #         self.device).eval()

        self.glmModel, self.glmTokenizer = load_model_and_tokenizer(self.model_path, self.device)

    def getRequest(self, input: dict) -> ChatCompletionRequest:
        request = ChatCompletionRequest(
            model=input["model"], messages=input["messages"],
            temperature=input["temperature"], top_p=input["top_p"],
            max_tokens=input["max_tokens"], stream=input["stream"],
            functions=input.get("functions", None),
            repetition_penalty=input.get("repetition_penalty", 1.1)
        )
        return request

    def inferFunction(self, input):
        # input.update({
        #     "functions": functions,  # 函数定义
        #     "model": model,  # 模型名称
        #     "messages": messages,  # 会话历史
        #     "stream": use_stream,  # 是否流式响应
        #     "max_tokens": 100,  # 最多生成字数
        #     "temperature": 0.0,  # 温度
        #     "top_p": 0.8,  # 采样概率
        # })
        request: ChatCompletionRequest = self.getRequest(input)
        return create_chat_completion(request, self.glmModel, self.glmTokenizer)
