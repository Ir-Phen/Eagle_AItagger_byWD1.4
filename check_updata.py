import requests
from packaging import version
import configparser  # 新增：用于解析config.ini文件

class VersionChecker:
    def __init__(self, global_config_path):
        """GitHub仓库配置"""
        self.repo_owner = r'Ir-Phen'
        self.repo_name = r'Eagle_AItagger_byWD1.4'
        self.global_config_path = global_config_path

    def get_local_version(self):
        """从config.ini获取本地版本信息"""
        config = configparser.ConfigParser()
        config.read(self.global_config_path)
        return config.get("Version", "version", fallback="0.0.0")

    def get_remote_version(self):
        """从GitHub获取版本远程信息"""
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("tag_name", "0.0.0")
        return "0.0.0"

    def check_for_update(self):
        """检查版本更新，可跳过"""
        local_version = self.get_local_version()
        remote_version = self.get_remote_version()
        if version.parse(remote_version) > version.parse(local_version):
            print(f"新版本可用: {remote_version} (当前版本: {local_version})")
            return True
        print("已是最新版本")
        return False

    def perform_update(self):
        """执行更新操作"""
        print("正在更新...")
        # 模拟更新操作
        print("更新完成")

    def update_local_version(self, new_version):
        """更新本地版本文件，保持其他配置信息不变"""
        config = configparser.ConfigParser()
        config.read(self.global_config_path)
        if not config.has_section("Version"):
            config.add_section("Version")
        config.set("Version", "local_version", new_version)
        with open(self.global_config_path, "w") as configfile:
            config.write(configfile)
        print(f"本地版本已更新为: {new_version}")

if __name__ == "__main__":