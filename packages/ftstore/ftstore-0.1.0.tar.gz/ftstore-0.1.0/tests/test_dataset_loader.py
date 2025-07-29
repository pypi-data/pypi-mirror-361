from pathlib import Path
import sys
print(f"项目根目录: {str(Path(__file__).parent.parent)}")
sys.path.insert(0, str(Path(__file__).parent.parent))
from ftstore.datasets import get_base_data_dir, list_datasets, get_dataset_metadata
from ftstore.datasets import load_data, get_data_dir_hash, clear_cache, clear_dataset_cache


# 1. 列出所有可用数据集
print("可用数据集:", list_datasets())

# 2. 获取iris数据集的元数据
iris_metadata = get_dataset_metadata("iris")
print("\nIris数据集元数据:")
print(f"特征数量: {len(iris_metadata['feature_names'])}")
print(f"目标列名: {iris_metadata['target_name']}")
print(f"特征名称: {iris_metadata['feature_names']}")

# 3. 加载iris数据集的不同格式

# 方式1：加载为DatasetBunch对象（默认）
iris_bunch = load_data("iris")
print("\nDatasetBunch格式:")
print(f"数据类型: {type(iris_bunch.data)}")
print(f"目标类型: {type(iris_bunch.target)}")
print(f"特征形状: {iris_bunch.data.shape}")
print(f"目标形状: {iris_bunch.target.shape}")
print(f"目标类别: {iris_bunch.target_names}")
print(f"完整数据框可用: {'是' if iris_bunch.frame is not None else '否'}")

# 方式2：加载为(X, y)元组（NumPy数组）
X, y = load_data("iris", return_X_y=True)
print("\n(X, y)元组格式 (NumPy):")
print(f"X类型: {type(X)}, 形状: {X.shape}")
print(f"y类型: {type(y)}, 形状: {y.shape}")

# 方式3：加载为(X, y)元组（DataFrame）
X_df, y_df = load_data("iris", return_X_y=True, as_frame=True)
print("\n(X, y)元组格式 (DataFrame):")
print(f"X类型: {type(X_df)}, 形状: {X_df.shape}")
print(f"y类型: {type(y_df)}, 形状: {y_df.shape}")
print("前5个样本:")
print(X_df.head())

# 方式4：加载为完整DataFrame
iris_df = load_data("iris", as_frame=True)
print("\n完整DataFrame格式:")
print(f"类型: {type(iris_df)}")
print(f"形状: {iris_df.shape}")
print("前5行:")
print(iris_df.head())

# 4.缓存路径和数据目录环境变量验证
# 清除旧缓存（可选）
from ftstore.datasets import clear_cache
clear_cache(force_delete=True)

# 先设置环境变量（必须在导入前）
import os
cache_dir = "D:/Python/python_work/jupyter_notebook/_skills_for_banks/_projects/one-line-alg/ftstore/.cached_datasets"
os.environ["DATASET_CACHE_DIR"] = cache_dir
data_dir = "C:/Users/ABDN/Desktop"
os.environ["FTSTORE_DATA_DIR"] = data_dir
# 导入并调用
from ftstore.datasets import load_data, get_memory

print(f"当前缓存目录配置: {os.environ.get('DATASET_CACHE_DIR')}")
print(f"实际使用的缓存目录: {get_memory().location}")

print("\n第一次加载会创建缓存...")
first_load = load_data("iris2")
print("数据集加载成功")
print("第二次加载会使用缓存...")
cached_load = load_data("iris2")

# clear_cache(force_delete=True)  # 清除旧缓存
clear_dataset_cache(dataset_name='iris2', force_delete=False)
