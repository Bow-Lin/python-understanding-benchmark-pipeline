"""
主模块

该模块负责协调整个pipeline的执行流程。
"""

import os
import sys
import json
from typing import Dict

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from project_collector import ProjectCollector
from docstring_remover import remove_docstrings_from_project
from symbol_extractor import extract_symbols_from_project, save_symbols_to_json


def main():
    """主函数，执行整个pipeline流程"""
    # 初始化项目收集器
    collector = ProjectCollector()
    
    # 收集项目
    print("开始收集项目...")
    collector.collect_projects()
    print("项目收集完成")
    
    # 获取项目路径
    project_paths = collector.get_project_paths()
    
    # 存储所有symbol的docstring
    all_symbols = {}
    
    # 处理每个项目
    for project_path in project_paths:
        project_name = os.path.basename(project_path)
        print(f"\n处理项目: {project_name}")
        
        # 提取项目中的symbol和docstring（在移除之前）
        print(f"提取项目 {project_name} 的symbol信息...")
        symbols = extract_symbols_from_project(project_path)
        all_symbols.update(symbols)
        
        # 移除项目中的docstring
        print(f"移除项目 {project_name} 中的docstring...")
        remove_docstrings_from_project(project_path)
        print(f"项目 {project_name} 处理完成")
    
    # 保存所有symbol的docstring
    output_path = "data/symbol_docstrings.json"
    print(f"\n保存symbol信息到 {output_path}...")
    save_symbols_to_json(all_symbols, output_path)
    print("所有项目处理完成")


if __name__ == "__main__":
    main()