import copy
from abc import ABC, abstractmethod
import logging
from typing import List
import os
from llmbench.inference.clients.request_data import Request
from llmbench.utils import PromptUtil

logger = logging.getLogger(__name__)


class Client(ABC):

    @abstractmethod
    def make_request(self, request: Request):
        pass

    @classmethod
    def format_prompt_for_history(cls, prompt: List):
        history = []
        new_prompt = copy.copy(prompt)
        for tmp in prompt:
            if tmp.get("role") == 'history':
                new_prompt.remove(tmp)
                history = tmp.get("content")
        return history, new_prompt

    @classmethod
    def format_prompt_for_multi_role(cls, prompt: List, file_type=None):
        """
        格式化prompt, 兼容原始格式与新格式数据类型, 返回文本内容与文件全路径
        :param prompt:
        :param file_type:
        :return:
        """
        if file_type is None:
            file_type = ["image"]
        file_paths = []
        data_prefix_path = PromptUtil.get_data_prefix_path(read_jsonl=True)
        if PromptUtil.is_multi_role(prompt):
            result = []
            for item in prompt[1:]:
                if item.get("role").startswith("user"):
                    if isinstance(item.get("content"), str):
                        result.append(f"用户：{item.get('content').strip()}\n")
                        if "file_path" in item:
                            if isinstance(item.get("file_path"), str):
                                file_paths.append(item.get("file_path"))
                            elif isinstance(item.get("file_path"), list):
                                file_paths.extend(item.get("file_path"))
                    elif isinstance(item.get("content"), list):
                        for per_con in item.get("content"):
                            if per_con.get("type", "") == "text":
                                result.append(f"用户：{per_con.get('content').strip()}\n")
                            if per_con.get("content") and per_con.get("type") in file_type:
                                file_paths.append(per_con.get("content"))
                elif item.get("role").startswith("assistant"):
                    result.append(f"系统：{item.get('content').strip()}\n")
            return [prompt[0], {"role": "user", "content": "".join(result)}], \
                   [os.path.join(data_prefix_path, file_path) for file_path in file_paths]
        else:
            result = []
            for item in prompt[1:]:
                if isinstance(item.get("content"), str):
                    result.append(str(item.get('content')).strip() + "\n")
                    if "file_path" in item:
                        if isinstance(item.get("file_path"), str):
                            file_paths.append(item.get("file_path"))
                        elif isinstance(item.get("file_path"), list):
                            file_paths.extend(item.get("file_path"))
                elif isinstance(item.get("content"), list):
                    for per_con in item.get("content"):
                        if per_con.get("type", "") == "text":
                            result.append(str(per_con.get('content')).strip() + "\n")
                        if per_con.get("content") and per_con.get("type") in file_type:
                            file_paths.append(per_con.get("content"))
            return [prompt[0], {"role": "user", "content": "".join(result)}], \
                   [os.path.join(data_prefix_path, file_path) for file_path in file_paths]