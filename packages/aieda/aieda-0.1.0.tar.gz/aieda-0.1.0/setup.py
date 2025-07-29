from setuptools import setup, find_packages
import os
from pathlib import Path

# 读取版本信息
def get_version():
    init_file = Path(__file__).parent / "aieda" / "__init__.py"
    if init_file.exists():
        with open(init_file) as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip('"\'')
    return "0.1.0"

# 读取README
def get_long_description():
    readme_file = Path(__file__).parent / "README.md"
    if readme_file.exists():
        return readme_file.read_text(encoding="utf-8")
    return "AI-Enhanced Electronic Design Automation Library with iEDA Integration"

# 读取requirements
def get_requirements():
    requirements_file = Path(__file__).parent / "requirements.txt"
    if requirements_file.exists():
        with open(requirements_file) as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    
    # 默认依赖
    return [
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "pyyaml>=5.4.0",
        "click>=8.0.0",
        "tqdm>=4.60.0",
    ]

setup(
    name="aieda",
    version=get_version(),
    author="yhqiu",
    author_email="qiuyihang23@mails.ucas.ac.cn",
    description="AI-Enhanced Electronic Design Automation Library with iEDA Integration",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/OSCC-Project/AiEDA",
    
    packages=find_packages(),
    
    # 包含所有数据文件
    package_data={
    },
    include_package_data=True,
    
    python_requires=">=3.8",
    install_requires=get_requirements(),
    
    # 可选依赖
    extras_require={
        # "dev": [
        #     "pytest>=6.0",
        #     "black>=21.0",
        #     "flake8>=3.8",
        #     "mypy>=0.800",
        # ],
        # "full": [
        #     "matplotlib>=3.3.0",
        #     "plotly>=5.0.0",
        #     "jupyter>=1.0.0",
        # ]
    },
    
    # 命令行工具
    entry_points={
        "console_scripts": [
            "aieda-flow=aieda.application.flow.run_iEDA_flow:main"
            # "aieda=aieda.cli:main",  # 如果你有CLI模块的话
        ],
    },
    
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research", 
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    
    keywords="eda, ieda, vlsi, synthesis, place-and-route, ai",
)