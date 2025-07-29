from .utils import load_dataset, DatasetBunch
from .registry import get_base_data_dir
from pathlib import Path
import warnings
from joblib import Memory
import os
import hashlib
import shutil
import glob

# 缓存版本，当数据结构变化时更新
CACHE_VERSION = "1.0"
# 声明全局memory变量，不立即初始化
memory = None

def get_memory():
    """动态获取缓存对象，确保使用最新的DATASET_CACHE_DIR"""
    global memory
    # 动态读取环境变量（每次调用都检查，确保实时生效）
    cache_dir = os.getenv("DATASET_CACHE_DIR", Path.home() / ".cached_datasets")
    cache_dir = Path(cache_dir).resolve()  # 转换为绝对路径，避免相对路径问题
    
    # 确保目录存在（即使路径包含转义字符或特殊符号）
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        warnings.warn(f"无法创建缓存目录 {cache_dir}，使用默认目录: {e}")
        cache_dir = Path.home() / ".cached_datasets"
        cache_dir.mkdir(parents=True, exist_ok=True)
    
    # 若缓存对象未初始化，或目录已变更，则重新创建
    if memory is None or Path(memory.location).resolve() != cache_dir:
        memory = Memory(location=str(cache_dir), verbose=0)  # 显式转换为字符串路径
    return memory

def get_data_dir_hash():
    """获取当前数据目录的哈希标识"""
    current_dir = get_base_data_dir()
    return hashlib.md5(str(current_dir.resolve()).encode()).hexdigest()[:8]  # 用绝对路径计算哈希

# 先定义原始函数（未装饰）
def _load_data(
    dataset_name: str, 
    return_X_y: bool = False, 
    as_frame: bool = False,
    warn_on_missing: bool = True,
    _cache_version: str = CACHE_VERSION,
    _data_dir_hash: str = None
):
    current_base_dir = get_base_data_dir()
    if _data_dir_hash is None:
        _data_dir_hash = get_data_dir_hash()

    # 加载数据时使用动态获取的目录
    df, metadata = load_dataset(dataset_name, current_base_dir)
    
    # 分离特征和目标
    target_col = metadata['target_name']
    target = df.pop(target_col)
    features = df.copy()
    
    # 处理缺失的元数据字段
    if 'target_names' not in metadata and warn_on_missing:
        warnings.warn(f"数据集 '{dataset_name}' 缺少 'target_names' 元数据")
    
    if 'DESCR' not in metadata and warn_on_missing:
        warnings.warn(f"数据集 '{dataset_name}' 缺少 'DESCR' 元数据")
    
    # 创建数据集对象
    bunch = DatasetBunch(
        data=features,
        target=target,
        feature_names=metadata['feature_names'],
        target_name=target_col,
        target_names=metadata.get('target_names'),
        DESCR=metadata.get('DESCR', f"{dataset_name} 数据集")
    )
    
    # 根据参数返回不同格式
    if return_X_y:
        if as_frame:
            return features, target
        return features.values, target.values
    
    if as_frame:
        return bunch.frame
    
    return bunch

# 动态生成装饰后的load_data（确保每次调用都使用最新的memory配置）
def load_data(*args, **kwargs):
    # 每次调用时获取最新的缓存装饰器
    cached_func = get_memory().cache(ignore=['_cache_version', '_data_dir_hash'])(_load_data)
    return cached_func(*args, **kwargs)

# 缓存管理函数
def clear_cache(force_delete: bool = False):
    """
    清除所有数据集缓存，支持强制删除目录并重建
    
    参数:
        force_delete: 是否强制删除整个缓存目录（而非仅清空内容）
    """
    mem = get_memory()
    cache_dir = Path(mem.location).resolve()
    
    if force_delete and cache_dir.exists():
        try:
            # 先删除整个缓存目录
            shutil.rmtree(cache_dir, ignore_errors=True)
            # 重建空目录（保持路径存在）
            # cache_dir.mkdir(parents=True, exist_ok=True)
            print(f"已强制删除缓存目录: {cache_dir}")
        except Exception as e:
            print(f"强制删除缓存目录失败: {e}")
            # 退回到普通清除方式
            mem.clear(warn=False)
            print(f"已使用普通方式清除缓存（缓存目录：{cache_dir}）")
    else:
        # 普通清除（仅删除缓存内容，保留目录）
        mem.clear(warn=False)
        print(f"已清除所有缓存（缓存目录：{cache_dir}）")
    
    # 重置memory对象（避免引用已删除的目录）
    global memory
    memory = None

def clear_dataset_cache(dataset_name: str, force_delete: bool = False):
    """
    清除特定数据集的缓存（适配实际路径：...\joblib\ftstore\datasets\loader\_load_data\哈希值）
    """
    try:
        cache_dir = Path(get_memory().location).resolve()
        
        # 实际缓存路径结构：
        # D:\...\.cached_datasets\joblib\ftstore\datasets\loader\_load_data\哈希值
        # 构建匹配规则：递归查找所有 _load_data 子目录（忽略中间层级和具体哈希值）
        cache_pattern = str(cache_dir / "joblib" / "**" / "_load_data" / "*")
        
        # 查找所有符合结构的缓存目录（启用递归匹配）
        matched_paths = glob.glob(cache_pattern, recursive=True)
        # print(f"匹配到的缓存路径: {matched_paths}")  # 调试用
        
        # 删除匹配的缓存目录
        for path in matched_paths:
            shutil.rmtree(path, ignore_errors=True)
            # print(f"已删除缓存目录: {path}")
        
        # 强制删除时额外清理 joblib 缓存索引
        if force_delete:
            get_memory().clear(warn=False)
            print(f"已强制清除所有缓存索引（缓存根目录：{cache_dir}）")
        
        print(f"已成功清除数据集 '{dataset_name}' 的缓存（共 {len(matched_paths)} 个目录）")
        
    except Exception as e:
        print(f"清除缓存失败: {e}")