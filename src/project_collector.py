"""
项目收集器模块

该模块负责克隆和管理开源项目。
"""

import os
import subprocess
from typing import List, Dict


class ProjectCollector:
    """负责收集和管理开源项目的类"""

    def __init__(self, projects_dir: str = "projects"):
        """
        初始化项目收集器

        :param projects_dir: 存放项目的目录路径
        """
        self.projects_dir = projects_dir
        self.projects = self._load_selected_projects()

    def _load_selected_projects(self) -> List[Dict[str, str]]:
        """
        加载预选的项目列表

        :return: 包含项目信息的字典列表
        """
        # 这里硬编码了一些知名的Python项目
        # 在实际项目中，这些信息可能会从配置文件中加载
        return [
            {"name": "flask", "url": "https://github.com/pallets/flask"},
            {"name": "requests", "url": "https://github.com/psf/requests"},
            {"name": "numpy", "url": "https://github.com/numpy/numpy"},
            {"name": "pandas", "url": "https://github.com/pandas-dev/pandas"},
            {"name": "django", "url": "https://github.com/django/django"},
            {"name": "scikit-learn", "url": "https://github.com/scikit-learn/scikit-learn"},
            {"name": "sqlalchemy", "url": "https://github.com/sqlalchemy/sqlalchemy"},
            {"name": "tensorflow", "url": "https://github.com/tensorflow/tensorflow"},
            {"name": "pytest", "url": "https://github.com/pytest-dev/pytest"},
            {"name": "beautifulsoup4", "url": "https://github.com/wention/BeautifulSoup4"},
        ]

    def collect_projects(self) -> None:
        """收集所有预选的项目"""
        # 确保项目目录存在
        os.makedirs(self.projects_dir, exist_ok=True)

        # 克隆每个项目
        for project in self.projects:
            self._clone_project(project)

    def _clone_project(self, project: Dict[str, str]) -> None:
        """
        克隆单个项目

        :param project: 包含项目信息的字典
        """
        project_path = os.path.join(self.projects_dir, project["name"])

        # 如果项目目录已存在，跳过克隆
        if os.path.exists(project_path):
            print(f"项目 {project['name']} 已存在，跳过克隆")
            return

        print(f"正在克隆项目 {project['name']}...")
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", project["url"], project_path],
                check=True,
                capture_output=True,
                text=True
            )
            print(f"成功克隆项目 {project['name']}")
        except subprocess.CalledProcessError as e:
            print(f"克隆项目 {project['name']} 失败: {e.stderr}")

    def get_project_paths(self) -> List[str]:
        """
        获取所有已克隆项目的路径

        :return: 项目路径列表
        """
        project_paths = []
        for project in self.projects:
            project_path = os.path.join(self.projects_dir, project["name"])
            if os.path.exists(project_path):
                project_paths.append(project_path)
        return project_paths