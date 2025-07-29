import abc
import json
import os
import random

import loguru

from finetune.GRPO.reward.parse import parse_reward_json
from finetune.GRPO.utils import extract_answer


class RewardDataset(abc.ABC):
    @abc.abstractmethod
    def load_datasets(self):
        """
        Load datasets from the specified source.
        :return: Loaded datasets.
        """
        pass

    @abc.abstractmethod
    def evaluate_reward(self, completions, **kwargs):
        """
        Evaluate the reward based on the loaded datasets.
        :return: Evaluated rewards.
        """
        pass


class DirectoryRewardDataset(RewardDataset):
    def __init__(self, folder_path: str, **kwargs):
        """
        HiveRewardDataset is a class to load datasets from a specified folder containing.
        :param folder_path: The path to the folder containing the datasets.
        :param kwargs: Additional keyword arguments, such as SYSTEM_PROMPT.
        """
        self.folder_path = folder_path
        self.system_prompt = kwargs.get('system_prompt', '')

    def _load_dataset_from_hive_reward(self):
        """
        Load QA datasets(Alpaca format.)
        and convert to chat format with system prompt.
        Add progress visualization and sampling logging.
        """
        from tqdm import tqdm
        import random
        from loguru import logger

        processed_data = []
        parsed_dataset = []

        hive_reward_files = []
        for root, dirs, files in os.walk(self.folder_path):
            for file in files:
                if file.endswith('.hive-reward.json'):
                    hive_reward_files.append(os.path.join(root, file))
        loguru.logger.info(f"Found {len(hive_reward_files)} files.")
        for file in tqdm(hive_reward_files, desc="Loading hive-reward files"):
            parsed_dataset.append(json.loads(open(file, 'r').read()))
        with tqdm(total=len(parsed_dataset),
                  desc="Converting samples",
                  bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{rate_fmt}]") as pbar:
            for idx, item in enumerate(parsed_dataset):
                # 合并指令和输入
                user_content = ""
                if item.get("topic", "").strip():
                    user_content += "\n" + item["topic"]

                # 构建对话格式
                formatted_item = {
                    "prompt": [
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    "answer": "",
                    "metadata": {
                        "hive-reward": json.dumps(item, ensure_ascii=False)  # 疑似Dataset中不会保持json结构，故而strify后传输
                    }
                }

                if random.random() < 0.001 or idx in (0, len(parsed_dataset) - 1):
                    logger.debug("\nSampled QA[{}]:\nSYSTEM: {}\nUSER: {}\nANSWER: {}",
                                 idx,
                                 self.system_prompt[:50] + "..." if len(
                                     self.system_prompt) > 50 else self.system_prompt,
                                 user_content[:100] + "..." if len(user_content) > 100 else user_content,
                                 "")

                processed_data.append(formatted_item)
                pbar.update(1)
                pbar.set_postfix_str(f"Last sampled: {idx}" if idx in (0, len(parsed_dataset) - 1) else "")

        # 数据集最终转换
        from datasets import Dataset
        return Dataset.from_list(processed_data)

    def load_datasets(self):
        return self._load_dataset_from_hive_reward()

    def evaluate_reward(self, completions, **kwargs):
        try:
            scores = []
            if random.random() < 0.01:
                loguru.logger.debug(f"Completions: {completions}")
                loguru.logger.debug(f"Len of completions: {len(completions)}")
            for completion in completions:
                assert 'metadata' in kwargs, "metadata is required."
                assert 'hive-reward' in kwargs['metadata'][0], f"hive-reward is required,now: {kwargs['metadata']}"
                metadata = kwargs['metadata']
                hive_reward_data = json.loads(metadata[0]['hive-reward'])
                scores.append(parse_reward_json(hive_reward_data=hive_reward_data, response=extract_answer(completion[0]['content'])))
            return scores
        except Exception as e:
            loguru.logger.trace(e)
            loguru.logger.error(f"Completions: {completions}")
            return [-1.0] * len(completions)


class FileRewardDataset(RewardDataset):
    def __init__(self, alpaca_dataset_path: str, **kwargs):
        """
        FileRewardDataset is a class to load datasets from a specified file containing.
        :param alpaca_dataset_path: The path to the Alpaca dataset file.
        :param kwargs: Additional keyword arguments, such as SYSTEM_PROMPT and SYSTEM_PROMPT_FREQ.
        """
        self.alpaca_dataset_path = alpaca_dataset_path
        self.system_prompt = kwargs.get('system_prompt', '')

    def _load_qa_dataset(self):
        """
        Load QA datasets(Alpaca format.)
        and convert to chat format with system prompt.
        Add progress visualization and sampling logging.
        """
        from tqdm import tqdm
        import random
        from loguru import logger

        with tqdm(total=1, desc="Loading dataset", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
            with open(self.alpaca_dataset_path) as file:
                alpaca_data = json.load(file)
            pbar.update(1)

        processed_data = []

        with tqdm(total=len(alpaca_data),
                  desc="Converting samples",
                  bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{rate_fmt}]") as pbar:
            for idx, item in enumerate(alpaca_data):
                # 合并指令和输入
                user_content = item["instruction"]
                if item.get("input", "").strip():
                    user_content += "\n" + item["input"]

                # 构建对话格式
                formatted_item = {
                    "prompt": [
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    "answer": item["output"]
                }

                # 采样记录（0.1%概率 + 首尾样本）
                if random.random() < 0.001 or idx in (0, len(alpaca_data) - 1):
                    logger.debug("\nSampled QA[{}]:\nSYSTEM: {}\nUSER: {}\nANSWER: {}",
                                 idx,
                                 self.system_prompt[:50] + "..." if len(
                                     self.system_prompt) > 50 else self.system_prompt,
                                 user_content[:100] + "..." if len(user_content) > 100 else user_content,
                                 item["output"][:100] + "..." if len(item["output"]) > 100 else item["output"])

                processed_data.append(formatted_item)
                pbar.update(1)
                pbar.set_postfix_str(f"Last sampled: {idx}" if idx in (0, len(alpaca_data) - 1) else "")

        # 数据集最终转换
        from datasets import Dataset
        return Dataset.from_list(processed_data)

    def load_datasets(self):
        return self._load_qa_dataset()

    def evaluate_reward(self, completions, **kwargs):
        # FIXME: We don't have any metadata that describe rewards
        return [-1.0] * len(completions)


class RemoteRewardDataset(RewardDataset):
    def __init__(self, remote_url: str, batch_size: int, **kwargs):
        self.remote_url = remote_url
        self.batch_size = batch_size
        self.system_prompt = kwargs.get('system_prompt', '')

    def load_datasets(self):
        import requests
        from tqdm import tqdm

        loaded_datasets = []

        for _ in tqdm(range(0, self.batch_size), desc="Loading remote datasets"):
            response = requests.get(f"{self.remote_url}/prompt")
            if response.status_code != 200:
                raise Exception(f"Failed to fetch prompt: {response.text}")
            parsed_dataset = response.json()
            loaded_datasets.append({
                "prompt": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": parsed_dataset['prompt']}
                ],
                "answer": "",
                "metadata": {
                    "remote-prompt-key": parsed_dataset['key']
                }
            })

        from datasets import Dataset
        return Dataset.from_list(loaded_datasets)

    def evaluate_reward(self, completions, **kwargs):
        import requests
        return [
            requests.post(f"{self.remote_url}/response",
                          json={
                              "key": kwargs['metadata'][0]['remote-prompt-key'],
                              "response": extract_answer(completion[0]['content'])
                          }).json()['score'] for completion in completions
        ]

def get_dataset_by_args(alpaca_dataset_path="", hive_reward_folder_path="", remote_url='', remote_batch_size=500, **kwargs):
    if alpaca_dataset_path:
        return FileRewardDataset(alpaca_dataset_path, **kwargs)
    if hive_reward_folder_path:
        return DirectoryRewardDataset(hive_reward_folder_path, **kwargs)
    if remote_url:
        return RemoteRewardDataset(remote_url, remote_batch_size, **kwargs)
    raise ValueError("Invalid arguments, you need to provide either `alpaca_dataset_path`, `hive_reward_folder_path`"
                     " or `remote_url`")
