from evalscope import TaskConfig, run_task
import os
import torch

# 确保所有GPU都可见
os.environ["CUDA_VISIBLE_DEVICES"] = "0,1,2,3"

# 设置内存优化环境变量
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

task_cfg = TaskConfig(
    model='/root/autodl-tmp/turn-djh/merged_model',
    datasets=['general_qa'],
    dataset_args={
        'general_qa': {
            "local_path": "/root/autodl-tmp/turn-djh/datasets/self_cognition.jsonl",
            "subset_list": ["self_cognition"]
        }
    },
    # 将model_args作为字典而不是字符串传递
    model_args={
        "device_map": "auto",
    }
)

run_task(task_cfg=task_cfg)
