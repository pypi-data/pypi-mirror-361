import os
import random
from datetime import datetime

import loguru
from peft import LoraConfig
from transformers import AutoModelForCausalLM
from transformers.trainer_utils import get_last_checkpoint
from trl import GRPOConfig

from finetune.GRPO.ModGRPOTrainer import MODGRPOTrainer
from finetune.GRPO.reward.dataset import RewardDataset


class HiveTrainer:
    def __init__(self,
                 dataset: RewardDataset,
                 model_name="Qwen2.5-0.5B-Instruct",
                 alpaca_dataset_path="",
                 hive_reward_folder_path="",
                 max_prompt_length=25565,
                 max_seq_length=128000,
                 logging_steps=1,
                 save_steps=50,
                 use_vllm=True,
                 report_to="tensorboard",
                 fp16=True,
                 learning_rate=5e-5,
                 num_train_epochs=9,
                 max_steps=10000,
                 train_model=['q_proj', 'k_proj', 'v_proj'],
                 LoRA_r=8,
                 LoRA_alpha=16,
                 per_device_train_batch_size=1,
                 gradient_checkpointing=True,
                 load_in_8bit=False,
                 vllm_gpu_memory_utilization=0.95,
                 vllm_server_host='localhost',
                 vllm_server_port=8000,
                 gradient_accumulation_steps=1,
                 vllm_mode="server",  # or colocate
                 vllm_tensor_parallel_size=2,
                 out_dir=None,
                 **kwargs):

        assert os.path.exists(model_name), f"Model {model_name} does not exist. Please check the path."

        self.hive_reward_dataset = None
        self.output_dir = model_name + "_trained" if out_dir is None else out_dir
        self.trainer = None
        self.model_name = model_name
        self.max_prompt_length = max_prompt_length
        self.max_seq_length = max_seq_length
        self.dataset = dataset

        self.logging_steps = logging_steps
        self.save_steps = save_steps
        self.use_vllm = use_vllm
        self.report_to = report_to
        self.fp16 = fp16
        self.learning_rate = learning_rate
        self.num_train_epochs = num_train_epochs
        self.max_steps = max_steps
        self.train_model = train_model
        self.LoRA_r = LoRA_r
        self.LoRA_alpha = LoRA_alpha
        self.per_device_train_batch_size = per_device_train_batch_size
        self.gradient_checkpointing = gradient_checkpointing
        self.load_in_8bit = load_in_8bit
        self.vllm_gpu_memory_utilization = vllm_gpu_memory_utilization
        self.vllm_server_host = vllm_server_host
        self.vllm_server_port = vllm_server_port
        self.gradient_accumulation_steps = gradient_accumulation_steps
        self.vllm_mode = vllm_mode
        self.vllm_tensor_parallel_size = vllm_tensor_parallel_size

        loguru.logger.info(f"Initializing HiveTrainer with the following parameters:{locals()}")

    def config_trainer(self):
        training_args = GRPOConfig(
            output_dir=self.output_dir,
            logging_steps=self.logging_steps,
            save_steps=self.save_steps,
            use_vllm=self.use_vllm,
            report_to=self.report_to,
            fp16=self.fp16,
            learning_rate=self.learning_rate,
            num_train_epochs=self.num_train_epochs,
            max_steps=self.max_steps,
            per_device_train_batch_size=self.per_device_train_batch_size,
            gradient_checkpointing=self.gradient_checkpointing,
            vllm_gpu_memory_utilization=self.vllm_gpu_memory_utilization,
            vllm_server_host=self.vllm_server_host,
            vllm_server_port=self.vllm_server_port,
            gradient_accumulation_steps=self.gradient_accumulation_steps,
            vllm_mode=self.vllm_mode,
            vllm_tensor_parallel_size=self.vllm_tensor_parallel_size,
            max_completion_length=self.max_seq_length
        )

        peft_config = LoraConfig(
            r=self.LoRA_r,
            lora_alpha=self.LoRA_alpha,
            target_modules=self.train_model,
            task_type="CAUSAL_LM",
            lora_dropout=0.05,
        )
        model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            load_in_8bit=self.load_in_8bit,
        )
        loguru.logger.debug(f"Load model done.")
        self.trainer = MODGRPOTrainer(
            model=model,
            reward_funcs=[
                self.dataset.evaluate_reward,  # general_reward
                # think_format_reward_func, TODO
                self.dump_conversation # only for conversation logging, always returns 0 for not particating in training
            ],
            args=training_args,
            train_dataset=self.dataset.load_datasets(),
            peft_config=peft_config,
        )
        loguru.logger.debug(f"Load trainer done.")

    def _output_dir_check(self):
        """
        Check the output_dir is existed?
        """
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            return False
        if len(os.listdir(self.output_dir)) == 0:
            return False
        return True

    def train(self):
        tmp_kwargs = {}
        if self._output_dir_check():
            last_checkpoint = get_last_checkpoint(self.output_dir)
            if last_checkpoint is not None:
                tmp_kwargs["resume_from_checkpoint"] = last_checkpoint
        self.config_trainer()
        self.trainer.train(**tmp_kwargs)
        save_name = f'lora_{datetime.now().strftime("%Y%m%d%H%M%S")}'
        # self.model.save_lora(save_name)
        # self.model.save_pretrained_merged("model", self.tokenizer, save_method="merged_16bit")

    def dump_conversation(self, completions, **kwargs):
        if random.randint(0, 200) > 1:
            return 0
        loguru.logger.debug(f"Dump conversation: {completions}")
        loguru.logger.debug(f"Total conversations: {len(completions)}")
        return 0
