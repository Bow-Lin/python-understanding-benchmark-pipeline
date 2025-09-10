"""
Symbol提取器模块

该模块负责从Python源代码中提取symbol信息和对应的docstring。
"""

import ast
import json
import os
from typing import Dict, Any, List


class SymbolExtractor(ast.NodeVisitor):
    """用于提取symbol信息和docstring的NodeVisitor"""

    def __init__(self, file_path: str, base_path: str):
        """
        初始化SymbolExtractor

        :param file_path: 当前处理的文件路径
        :param base_path: 项目基础路径
        """
        self.file_path = file_path
        self.base_path = base_path
        self.symbols = {}
        self.current_module = self._get_module_name(file_path)

    def _get_module_name(self, file_path: str) -> str:
        """
        根据文件路径获取模块名

        :param file_path: 文件路径
        :return: 模块名
        """
        # 计算相对于项目基础路径的相对路径
        rel_path = os.path.relpath(file_path, self.base_path)
        
        # 移除文件扩展名
        if rel_path.endswith('.py'):
            rel_path = rel_path[:-3]
        
        # 将路径分隔符替换为点号
        module_name = rel_path.replace(os.sep, '.')
        
        # 如果是__init__.py文件，模块名是其所在目录名
        if module_name.endswith('.__init__'):
            module_name = module_name[:-9]  # 移除.__init__
        
        return module_name

    def visit_Module(self, node: ast.Module) -> None:
        """
        访问模块节点并提取模块级docstring

        :param node: 模块节点
        """
        # 提取模块级docstring
        if (node.body and 
            isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and 
            isinstance(node.body[0].value.value, str)):
            docstring = node.body[0].value.value
            self.symbols[self.current_module] = docstring
        
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """
        访问类定义节点并提取类级docstring

        :param node: 类定义节点
        """
        # 构造类的完全限定名
        class_fqn = f"{self.current_module}.{node.name}"
        
        # 提取类级docstring
        if (node.body and 
            isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and 
            isinstance(node.body[0].value.value, str)):
            docstring = node.body[0].value.value
            self.symbols[class_fqn] = docstring
        
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """
        访问函数定义节点并提取函数级docstring

        :param node: 函数定义节点
        """
        # 构造函数的完全限定名
        function_fqn = f"{self.current_module}.{node.name}"
        
        # 提取函数级docstring
        if (node.body and 
            isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and 
            isinstance(node.body[0].value.value, str)):
            docstring = node.body[0].value.value
            self.symbols[function_fqn] = docstring
        
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """
        访问异步函数定义节点并提取函数级docstring

        :param node: 异步函数定义节点
        """
        # 构造异步函数的完全限定名
        function_fqn = f"{self.current_module}.{node.name}"
        
        # 提取异步函数级docstring
        if (node.body and 
            isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and 
            isinstance(node.body[0].value.value, str)):
            docstring = node.body[0].value.value
            self.symbols[function_fqn] = docstring
        
        self.generic_visit(node)


def extract_symbols_from_file(file_path: str, base_path: str) -> Dict[str, str]:
    """
    从Python文件中提取symbol信息和docstring

    :param file_path: Python文件路径
    :param base_path: 项目基础路径
    :return: symbol_fqn到docstring的映射字典
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    # 解析源代码为AST
    tree = ast.parse(source_code)
    
    # 提取symbol信息
    extractor = SymbolExtractor(file_path, base_path)
    extractor.visit(tree)
    
    return extractor.symbols


def extract_symbols_from_project(project_path: str) -> Dict[str, str]:
    """
    从项目中所有Python文件提取symbol信息和docstring

    :param project_path: 项目路径
    :return: symbol_fqn到docstring的映射字典
    """
    all_symbols = {}
    
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    symbols = extract_symbols_from_file(file_path, project_path)
                    all_symbols.update(symbols)
                    print(f"已处理文件: {file_path}")
                except Exception as e:
                    print(f"处理文件 {file_path} 时出错: {e}")
    
    return all_symbols


def save_symbols_to_json(symbols: Dict[str, str], output_path: str) -> None:
    """
    将symbol信息保存到JSON文件

    :param symbols: symbol_fqn到docstring的映射字典
    :param output_path: 输出文件路径
    """
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 保存到JSON文件
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(symbols, f, ensure_ascii=False, indent=2)
    
    print(f"已保存 {len(symbols)} 个symbol到 {output_path}")