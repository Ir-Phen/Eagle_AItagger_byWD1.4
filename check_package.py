import subprocess
import sys
from pathlib import Path
import pkg_resources

class package_manage:
    def __init__(self, requirements_path=None):
        self.sources = {
            "官方源": "https://pypi.org/simple/",
            # "中科大源": "https://mirrors.ustc.edu.cn/pypi/web/simple/",
            # "阿里云源": "https://mirrors.aliyun.com/pypi/simple/"
        }
        self.fastest_source = None
        self.requirements_path = requirements_path if requirements_path else Path(__file__).resolve().parent / 'requirements.txt'

    def read_requirements(self, file_path):
        '''读取requirements.txt文件'''
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                requirements = file.read().splitlines()
                return [req.strip() for req in requirements if req.strip()]
        except FileNotFoundError:
            print(f"文件 {file_path} 未找到。")
            return []

    def install_dependencies(self, missing_dependencies, source=None):
        """安装缺失的依赖项"""
        for requirement in missing_dependencies:
            print(f"正在安装: {requirement}...")
            try:
                cmd = [sys.executable, "-m", "pip", "install", requirement]
                if source:
                    cmd.extend(["--index-url", source])
                subprocess.check_call(cmd)
                print(f"成功安装: {requirement}")
            except Exception as e: 
                print(f"安装失败: {requirement} - {e}")

    def check_dependencies(self, requirements):
        '''检查依赖是否安装'''
        missing = []
        for req in requirements:
            try:
                pkg_resources.require(req)
            except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
                missing.append(req)
        return missing

def check_package(requirements_path):
    package_checker = package_manage(requirements_path)
    requirements = package_checker.read_requirements(package_checker.requirements_path)
    if not requirements:
        print("无依赖项需要检查。")
        return
    missing = package_checker.check_dependencies(requirements)
    if missing:
        print("缺失依赖:", missing)
        fastest_source = package_checker.test_source_speed()
        if fastest_source:
            source_url = package_checker.sources[fastest_source]
            package_checker.install_dependencies(missing, source_url)
    else:
        print("所有依赖已安环境配置正常。")

if __name__ == "__main__":
    requirements_path = "requirements.txt"
    check_package(requirements_path)