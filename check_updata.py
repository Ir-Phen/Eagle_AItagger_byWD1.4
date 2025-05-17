import requests
from packaging import version
import configparser

class VersionChecker:
    def __init__(self, config_data: configparser.ConfigParser, config_path: str):
        """接收已解析的config_data和配置文件路径"""
        self.config_data = config_data
        self.config_path = config_path  # 用于保存更新后的配置
        self.github_url = 'https://github.com/Ir-Phen/Eagle_AItagger_byWD1.4'

    def get_local_version(self) -> str:
        """直接从config_data获取本地版本"""
        return self.config_data.get("Version", "version", fallback="0.0.0")

    def get_remote_version(self) -> str:
        """从GitHub获取远程版本（逻辑保持不变）"""
        raw_url = "https://raw.githubusercontent.com/Ir-Phen/Eagle_AItagger_byWD1.4/main/config.ini"
        try:
            response = requests.get(raw_url, timeout=10)
            response.raise_for_status()
            remote_config = configparser.ConfigParser()
            remote_config.read_string(response.text)
            return remote_config.get("Version", "version", fallback="0.0.0"), remote_config.get("Version", "update_notes", fallback='更新信息获取失败。')
        
        except Exception as e:
            print(f'获取远程版本失败: {e}')
            return (None, None)
        
    def check_for_update(self) -> bool:
        """检查版本更新"""
        local_version = self.get_local_version()
        remote_version, update_notes = self.get_remote_version()

        if remote_version is None:  # 远程获取失败
            print(f"可手动检查更新: {self.github_url}")
            return False
        
        if version.parse(remote_version) < version.parse(local_version):
            print("警告：本地版本高于远程版本，请检查配置！")
            return False
    
        if version.parse(remote_version) > version.parse(local_version):
            print(f"新版本可用: {remote_version} (当前版本: {local_version}\n更新内容:{update_notes})")
            user_choice = input("发现新版本，是否更新？(y/n): ")
            if user_choice.lower() == 'y':
                self.update_local_version(remote_version, update_notes)
                return True
            else:
                print("已跳过更新。")
                return False
        print("已是最新版本")
        return False

    def update_local_version(self, new_version: str, update_notes: str):
        """更新config_data并保存到文件"""
        if not self.config_data.has_section("Version"):
            self.config_data.add_section("Version")
        self.config_data.set("Version", "version", new_version)
        self.config_data.set("Version", "update_notes", update_notes)  # 使用传入的更新说明
        try:
            with open(self.config_path, "w", encoding='utf-8') as f:
                self.config_data.write(f)
        except PermissionError:
            print("错误：无权限写入配置文件！")
        print(f"本地版本已更新至: {new_version}\n更新说明已保存")

    
# 入口函数适配
def on_check_update(config_data: configparser.ConfigParser, config_path: str) -> VersionChecker:
    """主入口：传入已解析的config_data和文件路径"""
    checker = VersionChecker(config_data, config_path)
    checker.check_for_update()
    return checker

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config_path = "config.ini"
    config.read(config_path, encoding='utf-8')
    
    checker = on_check_update(config, config_path)