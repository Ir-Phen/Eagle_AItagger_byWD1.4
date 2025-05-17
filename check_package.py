import time
import requests
import subprocess
import sys
from pathlib import Path
import pkg_resources

class package_manage:
    def __init__(self,requirements_path = None):
        self.sources = {
        "官方源": "https://pypi.org/simple/"
        # "中科大源": "https://mirrors.ustc.edu.cn/pypi/web/simple/"
        # "阿里云源": "https://mirrors.aliyun.com/pypi/simple/"
        }
        self.fastest_source = None
        self.requirements_path = requirements_path if requirements_path else Path(__file__).resolve().parent / 'requirements.txt'

    def test_source_speed(sources):
        '''测试各个源的速度'''
        fastest_source = None
        fastest_time = float('inf')
        
        for source_name, source_url in sources.items():
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
        
        return fastest_source

    def set_pip_source(source):
        '''设置pip源为当前下载的配置'''
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--index-url", source])
            print(f"成功设置pip源为当前下载的配置: {source}")
        except subprocess.CalledProcessError as e:
            print(f"设置pip源失败: {e}")

    def read_requirements(file_path):
        '''读取requirements.txt文件'''
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                requirements = file.read().splitlines()
                return requirements
        except FileNotFoundError:
            print(f"文件 {file_path} 未找到。")
            return []
    
    def install_dependencies(self, missing_dependencies, source=None):
        """安装缺失的依赖项，并指定 pip 源"""
        for requirement in missing_dependencies:
            print(f"正在尝试安装: {requirement}...")
            try:
                cmd = [sys.executable, "-m", "pip", "install", requirement]
                if source:  # 如果传入了源，则添加 --index-url
                    cmd.extend(["--index-url", source])
                subprocess.check_call(cmd)
                print(f"成功安装: {requirement}")
            except subprocess.CalledProcessError as e:
                print(f"安装 {requirement} 失败: {e}")

    def install_dependencies(self, missing_dependencies):
        '''安装缺失的依赖项'''
        for requirement in missing_dependencies:
            print(f"正在尝试安装: {requirement}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", requirement])
                print(f"成功安装: {requirement}")
            except subprocess.CalledProcessError as e:
                print(f"安装 {requirement} 失败: {e}")

def check_package(requirements_path):
    package_checker = package_manage()
    requirements = package_checker.read_requirements(package_checker.requirements_path)
    missing_dependencies = package_checker.check_dependencies(requirements)
    if missing_dependencies:
        fastest_source = package_checker.test_source_speed(package_checker.sources)
        if fastest_source:
            package_checker.install_dependencies(missing_dependencies, package_checker.sources[fastest_source])
    else:
        print("环境配置正常")

if __name__ == "__main__":
    requirements_path = "E:\\GitHub\\Eagle_AItagger_byWD1.4\\requirements.txt"  # 或者你的 requirements.txt 文件的实际路径
    check_package(requirements_path)