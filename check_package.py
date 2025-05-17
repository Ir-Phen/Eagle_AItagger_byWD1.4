import time
import requests
import subprocess
import sys
from pathlib import Path
import pkg_resources

class package_manage:
    def __init__(self, requirements_path=None):
        self.sources = {
            "官方源": "https://pypi.org/simple/",
            "中科大源": "https://mirrors.ustc.edu.cn/pypi/web/simple/",
            "阿里云源": "https://mirrors.aliyun.com/pypi/simple/"
        }
        self.fastest_source = None
        self.requirements_path = requirements_path if requirements_path else Path(__file__).resolve().parent / 'requirements.txt'

    def test_source_speed(self):
        '''测试各个源的速度'''
        fastest_source = None
        fastest_time = float('inf')
        
        for source_name, source_url in self.sources.items():
            start_time = time.time()
            try:
                response = requests.get(source_url, timeout=5)
                if response.status_code == 200:
                    elapsed_time = time.time() - start_time
                    print(f"{source_name} 响应时间: {elapsed_time:.2f}秒")
                    if elapsed_time < fastest_time:
                        fastest_time = elapsed_time
                        fastest_source = source_name
            except requests.RequestException as e:
                print(f"请求 {source_name} 失败: {e}")
        
        if fastest_source:
            print(f"速度最快的源是: {fastest_source}")
        else:
            print("没有找到可用的源。")
        self.fastest_source = fastest_source
        return fastest_source

    @staticmethod
    def set_pip_source(source):
        '''设置pip源'''
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--index-url", source])
            print(f"成功设置pip源: {source}")
        except subprocess.CalledProcessError as e:
            print(f"设置pip源失败: {e}")

    def read_requirements(self, file_path):
        '''读取requirements.txt文件'''
        try:
            with open(file_path, 'r', encoding='utf-16') as file:
                requirements = file.read().splitlines()
                return [req.strip() for req in requirements if req.strip()]
        except FileNotFoundError:
            print(f"文件 {file_path} 未找到。")
            return []

    def install_dependencies(self, missing_dependencies, source=None):
        """安装缺失的依赖项，可选指定源"""
        for requirement in missing_dependencies:
            print(f"正在安装: {requirement}...")
            try:
                cmd = [sys.executable, "-m", "pip", "install", requirement]
                if source:
                    cmd.extend(["--index-url", source])
                subprocess.check_call(cmd)
                print(f"成功安装: {requirement}")
            except subprocess.CalledProcessError as e:
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
    requirements_path = "E:\\GitHub\\Eagle_AItagger_byWD1.4\\requirements.txt"
    check_package(requirements_path)