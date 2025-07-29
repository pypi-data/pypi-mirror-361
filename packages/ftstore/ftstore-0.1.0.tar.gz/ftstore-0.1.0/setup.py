from setuptools import setup, find_packages
import os

# 读取README内容
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 获取版本号
def get_version():
    here = os.path.abspath(os.path.dirname(__file__))
    version_file = os.path.join(here, "ftstore", "version.py")
    version = {}
    with open(version_file, "r", encoding="utf-8") as f:
        exec(f.read(), version)
    return version["__version__"]

setup(
    name="ftstore",
    version=get_version(),
    author="chrisli-llb",
    author_email="871266889@qq.com",
    description="Advanced local dataset management for machine learning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chrisli-llb/ftstore",
    packages=find_packages(include=["ftstore", "ftstore.*"]),
    package_data={
        "ftstore.datasets": [
            "data/*", 
            "data/**/*"
        ]
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pandas>=1.0",
        "numpy>=1.18",
        "requests>=2.25",
        "joblib>=1.0",
    ],
    extras_require={
        "parquet": ["pyarrow>=3.0"],
        "hdf5": ["tables>=3.6"],
        "excel": ["openpyxl>=3.0", "xlrd>=2.0"],
        "feather": ["pyarrow>=3.0"],
        "full": [
            "pyarrow>=3.0", 
            "tables>=3.6", 
            "openpyxl>=3.0", 
            "xlrd>=2.0"
        ],
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=3.0",
            "twine>=4.0",
            "wheel>=0.37",
            "flake8>=4.0",
            "black>=22.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "ftstore-clear-cache=ftstore.datasets:clear_cache_cli"
        ]
    },
    project_urls={
        "Bug Tracker": "https://github.com/chrisli-llb/ftstore/issues",
        "Documentation": "https://github.com/chrisli-llb/ftstore/wiki",
        "Source Code": "https://github.com/chrisli-llb/ftstore",
    },
)