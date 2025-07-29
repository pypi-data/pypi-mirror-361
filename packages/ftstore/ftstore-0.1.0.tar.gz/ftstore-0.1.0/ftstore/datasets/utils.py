import os
import json
import pandas as pd
from pathlib import Path
from dataclasses import dataclass
import numpy as np
from typing import Union, Tuple
import warnings

@dataclass
class DatasetBunch:
    """数据集容器类，包含数据集的所有信息"""
    data: Union[pd.DataFrame, np.ndarray]
    target: Union[pd.Series, np.ndarray]
    feature_names: list
    target_name: str
    target_names: list = None
    DESCR: str = None
    frame: pd.DataFrame = None
    
    def __post_init__(self):
        """初始化后处理，创建完整的数据框"""
        if isinstance(self.data, pd.DataFrame) and isinstance(self.target, pd.Series):
            self.frame = self.data.assign(**{self.target_name: self.target})
        elif self.frame is None:
            # 如果输入不是DataFrame，尝试创建
            try:
                df = pd.DataFrame(self.data, columns=self.feature_names)
                df[self.target_name] = self.target
                self.frame = df
            except Exception:
                self.frame = None

def load_dataset(dataset_name: str, base_dir: Path) -> Tuple[pd.DataFrame, dict]:
    """
    加载数据集和元数据（支持多种文件格式）
    """
    dataset_dir = base_dir / dataset_name
    
    if not dataset_dir.exists():
        raise FileNotFoundError(f"数据集目录不存在: {dataset_dir}")
    
    # 加载元数据
    metadata_path = dataset_dir / "metadata.json"
    if not metadata_path.exists():
        raise FileNotFoundError(f"元数据文件不存在: {metadata_path}")
    
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    # 支持的文件格式列表
    SUPPORTED_EXTENSIONS = [
        '.csv', '.parquet', '.feather', '.h5', '.hdf5', 
        '.pkl', '.pickle', '.xls', '.xlsx', '.json',
        '.data', '.txt', '.tsv'
    ]
    
    # 查找数据文件
    data_files = [f for f in os.listdir(dataset_dir) 
                 if any(f.endswith(ext) for ext in SUPPORTED_EXTENSIONS) and f != "metadata.json"]  # f.startswith('data') and 
    # print('data_files', data_files)
    
    if not data_files:
        print('data_files', data_files)
        raise FileNotFoundError(f"在 {dataset_dir} 中未找到支持的数据文件")
    
    if len(data_files) > 1:
        # 尝试优先选择Parquet或Feather格式
        priority_formats = ['.parquet', '.feather', '.h5', '.csv']
        for fmt in priority_formats:
            for f in data_files:
                if f.endswith(fmt):
                    data_file = f
                    break
            else:
                continue
            break
        else:
            data_file = data_files[0]  # 默认选择第一个文件
        warnings.warn(f"在 {dataset_dir} 中找到多个数据文件，已选择: {data_file}")
    else:
        data_file = data_files[0]
    
    file_path = dataset_dir / data_file
    
    # 根据文件类型加载数据
    try:
        # 使用完整路径 file_path 而不是文件名 data_file
        if file_path.suffix == '.csv':
            df = pd.read_csv(file_path)
        elif file_path.suffix == '.parquet':
            df = pd.read_parquet(file_path)
        elif file_path.suffix == '.feather':
            df = pd.read_feather(file_path)
        elif file_path.suffix in ['.h5', '.hdf5']:
            with pd.HDFStore(file_path, 'r') as store:
                datasets = store.keys()
                if datasets:
                    df = store[datasets[0]]
                else:
                    raise ValueError("HDF5文件中没有找到数据集")
        elif file_path.suffix in ['.pkl', '.pickle']:
            df = pd.read_pickle(file_path)
        elif file_path.suffix in ['.xls', '.xlsx']:
            df = pd.read_excel(file_path)
        elif file_path.suffix == '.json':
            df = pd.read_json(file_path)
        elif file_path.suffix in ['.data', '.txt', '.tsv']:
            # 使用完整路径 file_path 而不是文件名 data_file
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
            
            # 检测分隔符
            if '\t' in first_line:
                sep = '\t'
            elif ';' in first_line:
                sep = ';'
            elif ',' in first_line:
                sep = ','
            else:
                sep = None  # 让pandas自动检测
                
            df = pd.read_csv(file_path, sep=sep, encoding='utf-8', engine='python')
        else:
            raise ValueError(f"不支持的文件格式: {file_path.suffix}")
    except Exception as e:
        raise RuntimeError(f"加载文件 {file_path} 失败: {str(e)}")
    
    # 验证元数据
    required_fields = ['feature_names', 'target_name']
    for field in required_fields:
        if field not in metadata:
            raise ValueError(f"元数据缺少必要字段: '{field}'")
    
    # 验证目标列是否存在
    if metadata['target_name'] not in df.columns:
        # 尝试不区分大小写匹配
        target_col = metadata['target_name'].lower()
        matching_cols = [col for col in df.columns if col.lower() == target_col]
        
        if matching_cols:
            # 更新元数据使用实际列名
            metadata['target_name'] = matching_cols[0]
        else:
            available_cols = ", ".join(df.columns)
            raise KeyError(
                f"目标列 '{metadata['target_name']}' 不存在于数据中\n"
                f"可用列: {available_cols}"
            )
    
    # 验证特征数量
    if metadata['feature_names'] and len(metadata['feature_names']) != (df.shape[1] - 1):
        warnings.warn(
            f"元数据中的特征数量({len(metadata['feature_names'])}) "
            f"与数据特征数({df.shape[1] - 1})不匹配"
        )
        # 如果特征名为空，尝试使用数据列名
        if not metadata['feature_names']:
            metadata['feature_names'] = [col for col in df.columns if col != metadata['target_name']]
    
    return df, metadata