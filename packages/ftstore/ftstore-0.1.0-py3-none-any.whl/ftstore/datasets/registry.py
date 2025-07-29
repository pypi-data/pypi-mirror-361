import os
import json
from pathlib import Path
import warnings

def get_base_data_dir():
    """获取数据集基础目录，优先级：
    1. FTSTORE_DATA_DIR 环境变量
    2. 默认项目目录 (ftstore/datasets/data)
    """
    # 检查环境变量
    env_data_dir = os.getenv("FTSTORE_DATA_DIR")
    if env_data_dir:
        env_path = Path(env_data_dir)
        if env_path.exists() and env_path.is_dir():
            return env_path
        warnings.warn(f"环境变量 FTSTORE_DATA_DIR 指定的目录不存在: {env_path}. 使用默认目录")
    
    # 默认项目目录
    default_dir = Path(__file__).parent / 'data'
    # print(f'使用默认数据集目录: {default_dir}')
    return default_dir

def list_datasets() -> list:
    """列出所有可用的数据集"""
    base_dir = get_base_data_dir()  # 动态获取当前目录
    if not base_dir.exists():
        return []
    
    return [d.name for d in base_dir.iterdir() if d.is_dir()]

def get_dataset_metadata(dataset_name: str) -> dict:
    """获取数据集的元数据"""
    base_dir = get_base_data_dir()  # 动态获取当前目录
    dataset_dir = base_dir / dataset_name
    
    if not dataset_dir.exists():
        raise ValueError(f"数据集 '{dataset_name}' 不存在")
    
    metadata_path = dataset_dir / "metadata.json"
    if not metadata_path.exists():
        raise FileNotFoundError(f"元数据文件不存在: {metadata_path}")
    
    with open(metadata_path, 'r', encoding='utf-8') as f:
        return json.load(f)