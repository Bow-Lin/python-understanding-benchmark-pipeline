# Python Understanding Benchmark Pipeline

## 项目概述

这是一个用于评估大型语言模型（LLM）理解 Python 项目代码能力的基准测试管道。该项目通过以下方式评估LLM：

1. 收集约10个生产级别的开源 Python 项目（如 Flask），这些项目具有清晰规范的 docstring
2. 从这些项目中移除原始 docstring
3. 为每个符号（类、函数、方法）生成对应的docstring存储，以symbol_fqn为键
4. 为后续评估做准备，另一个程序将使用这些数据为每个symbol创建docstring，并通过symbol_fqn获取pipeline的docstring进行比较

## 目录结构

```
python-understanding-benchmark-pipeline/
├── README.md
├── requirements.txt
├── pyproject.toml
├── projects/
│   └── [收集的开源项目]
├── data/
│   └── symbol_docstrings.json
└── src/
    ├── __init__.py
    ├── main.py
    ├── project_collector.py
    ├── docstring_remover.py
    └── symbol_extractor.py
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

```bash
python -m src.main
```

## 工作流程

1. `ProjectCollector` 收集预定义的10个开源Python项目
2. `SymbolExtractor` 提取每个项目中所有符号（模块、类、函数、方法）的原始docstring，并以symbol_fqn为键存储
3. `DocstringRemover` 移除所有项目中的docstring
4. 最终结果保存在 `data/symbol_docstrings.json` 文件中，供后续评估使用

## 核心组件

### 1. 项目收集器 (ProjectCollector)
负责克隆和管理开源项目，当前硬编码了10个知名的Python项目：
- Flask
- Requests
- NumPy
- Pandas
- Django
- Scikit-learn
- SQLAlchemy
- TensorFlow
- Pytest
- Beautiful Soup 4

### 2. Symbol提取器 (SymbolExtractor)
负责从Python源代码中提取symbol信息和对应的docstring：
- 使用AST解析源代码
- 提取模块、类、函数、方法的docstring
- 以symbol_fqn为键存储docstring
- 将结果保存到JSON文件

### 3. Docstring剥离器 (DocstringRemover)
负责从Python源代码中移除docstring：
- 使用AST解析源代码
- 移除模块、类、函数、方法的docstring
- 将处理后的代码写回原文件

### 4. 主控制器 (Main)
负责协调整个pipeline的执行流程：
- 初始化项目收集器
- 收集项目
- 处理每个项目（提取docstring、移除docstring）
- 保存结果

## 技术栈

- Python: 主要编程语言 (要求 >=3.12)
- Git: 版本控制系统
- AST: Python 标准库，用于解析源代码
- astor: 用于将AST转换回源代码的第三方库

## 开发约定

- 使用 MIT 许可证
- 遵循标准的 Python 项目结构
- 使用 Git 进行版本控制
- 通过 `.gitignore` 文件管理忽略的文件和目录
- 遵循 PEP 8 代码风格指南
- 为所有公共接口编写清晰的 docstring

## 输出格式

项目将生成以下主要输出：

1. `data/symbol_docstrings.json`: 包含symbol_fqn与原始docstring映射关系的JSON文件
2. 剥离docstring后的项目代码，存储在`projects/`目录中
