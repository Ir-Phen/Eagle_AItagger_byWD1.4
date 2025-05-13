import os
import requests
from packaging import version
import configparser  # 新增：用于解析config.ini文件
import argparse

# GitHub仓库配置
GITHUB_REPO_URL = "https://api.github.com/repos/{owner}/{repo}/contents/version_info.md"
GITHUB_OWNER = "your_username"
GITHUB_REPO = "your_repository"

class VersionChecker:
    @staticmethod
    def get_local_version():
        """从config.ini获取本地版本信息"""
        try:
            config = configparser.ConfigParser()
            config.read('config.ini')
            return config['version']['version']
        except Exception as e:
            print(f"获取本地版本信息失败: {e}")
            return "1.0"  # 默认版本

    @staticmethod
    def get_local_version_notes():
        """从config.ini获取本地版本更新记录"""
        try:
            config = configparser.ConfigParser()
            config.read('config.ini')
            update_notes = config['version']['update_notes']
            return {config['version']['version']: update_notes}
        except Exception as e:
            print(f"获取本地版本更新记录失败: {e}")
            return {"1.0": "初始发布版本"}  # 默认更新记录

    @staticmethod
    def get_remote_version():
        """从GitHub获取版本远程信息"""
        try:
            url = GITHUB_REPO_URL.format(owner=GITHUB_OWNER, repo=GITHUB_REPO)
            response = requests.get(url)
            response.raise_for_status()  # 检查请求是否成功
            
            # 假设版本信息存储在GitHub仓库的特定文件中
            version_data = response.json()
            file_content = version_data.get("content", "")
            
            # 解码base64编码的内容
            import base64
            decoded_content = base64.b64decode(file_content).decode('utf-8')
            
            # 解析版本信息（假设文件内容是JSON格式）
            import json
            version_info = json.loads(decoded_content)
            return version_info.get("version", VersionChecker.get_local_version()), version_info.get("update_notes", {})
        except Exception as e:
            print(f"获取远程版本信息失败: {e}")
            return VersionChecker.get_local_version(), {}

    @classmethod
    def check_for_updates(cls):
        """检查版本更新"""
        local_ver = cls.get_local_version()
        remote_ver, remote_notes = cls.get_remote_version()
        
        # 如果本地版本较低，建议更新
        if version.parse(local_ver) < version.parse(remote_ver):
            print(f"检测到新版本: {remote_ver} (当前版本: {local_ver})")
            print("更新内容:")
            
            # 显示当前版本之后的所有更新内容
            sorted_notes = sorted(remote_notes.items(), key=lambda x: version.parse(x[0]))
            update_found = False
            
            for ver, note in sorted_notes:
                if version.parse(ver) > version.parse(local_ver):
                    print(f"- {ver}: {note}")
                    update_found = True
            
            if update_found:
                print("\n建议您进行更新。要更新，可以运行:")
                print("  python update_script.py --update")
            else:
                print("没有找到比当前版本更新的内容")
        else:
            print(f"您的版本 ({local_ver}) 已是最新版本")

    @classmethod
    def perform_update(cls):
        """执行更新操作"""
        print("执行更新操作...")
        # 这里可以添加具体的更新逻辑，如下载新版本或更新本地文件
        remote_ver, _ = cls.get_remote_version()
        print(f"更新到版本: {remote_ver}")
        # 举例：更新本地版本文件
        cls.update_local_version_file(remote_ver)
        
        print("更新完成！")

    @classmethod
    def update_local_version_file(cls, new_version):
        """更新本地版本文件"""
        try:
            config = configparser.ConfigParser()
            config.read('config.ini')
            config['version']['version'] = new_version
            config['version']['update_notes'] = f"r'更新到版本 {new_version}'"
            
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
            print("本地版本文件已更新")
        except Exception as e:
            print(f"更新本地版本文件失败: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="版本检查工具")
    parser.add_argument('--check', action='store_true', help='检查版本更新')
    parser.add_argument('--update', action='store_true', help='执行更新操作')
    
    args = parser.parse_args()
    
    if args.check:
        VersionChecker.check_for_updates()
    elif args.update:
        VersionChecker.perform_update()
    else:
        parser.print_help()