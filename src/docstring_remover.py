"""
Docstring移除器模块

该模块负责从Python源代码中移除docstring。
"""

import ast
import os
from typing import List, Dict, Tuple


class DocstringRemover(ast.NodeTransformer):
    """用于移除AST中docstring的NodeTransformer"""

    def visit_Module(self, node: ast.Module) -> ast.AST:
        """
        访问模块节点并移除模块级docstring

        :param node: 模块节点
        :return: 修改后的节点
        """
        # 移除模块的第一个表达式语句（如果它是docstring）
        if (node.body and 
            isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and 
            isinstance(node.body[0].value.value, str)):
            node.body = node.body[1:]
        
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST:
        """
        访问类定义节点并移除类级docstring

        :param node: 类定义节点
        :return: 修改后的节点
        """
        # 移除类的第一个表达式语句（如果它是docstring）
        if (node.body and 
            isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and 
            isinstance(node.body[0].value.value, str)):
            node.body = node.body[1:]
        
        self.generic_visit(node)
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        """
        访问函数定义节点并移除函数级docstring

        :param node: 函数定义节点
        :return: 修改后的节点
        """
        # 移除函数的第一个表达式语句（如果它是docstring）
        if (node.body and 
            isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and 
            isinstance(node.body[0].value.value, str)):
            node.body = node.body[1:]
        
        self.generic_visit(node)
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
        """
        访问异步函数定义节点并移除函数级docstring

        :param node: 异步函数定义节点
        :return: 修改后的节点
        """
        # 移除异步函数的第一个表达式语句（如果它是docstring）
        if (node.body and 
            isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and 
            isinstance(node.body[0].value.value, str)):
            node.body = node.body[1:]
        
        self.generic_visit(node)
        return node


def remove_docstrings_from_file(file_path: str) -> str:
    """
    从Python文件中移除所有docstring

    :param file_path: Python文件路径
    :return: 移除docstring后的源代码
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    # 解析源代码为AST
    tree = ast.parse(source_code)
    
    # 移除docstring
    transformer = DocstringRemover()
    new_tree = transformer.visit(tree)
    
    # 将修改后的AST转换回源代码
    # 注意：ast.unparse在Python 3.9+可用，对于低版本可能需要其他方法
    try:
        new_source_code = ast.unparse(new_tree)
    except AttributeError:
        # 对于Python 3.8及以下版本，使用astor库
        import astor
        new_source_code = astor.to_source(new_tree)
    
    return new_source_code


def remove_docstrings_from_project(project_path: str) -> None:
    """
    从项目中所有Python文件移除docstring

    :param project_path: 项目路径
    """
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    new_source_code = remove_docstrings_from_file(file_path)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_source_code)
                    print(f"已处理文件: {file_path}")
                except Exception as e:
                    print(f"处理文件 {file_path} 时出错: {e}")