import requests
from packaging import version
import configparser

class VersionChecker:
    def __init__(self, config_data: configparser.ConfigParser, config_path: str):
        self.config_data = config_data
        self.config_path = config_path
        self.github_url = 'https://github.com/Ir-Phen/Eagle_AItagger_byWD1.4'

    def get_local_version(self) -> str:
        return self.config_data.get("Version", "version", fallback="0.0.0")

    def get_remote_version(self) -> tuple:
        raw_url = "https://raw.githubusercontent.com/Ir-Phen/Eagle_AItagger_byWD1.4/main/config.ini"
        try:
            response = requests.get(raw_url, timeout=10)
            response.raise_for_status()
            remote_config = configparser.ConfigParser()
            remote_config.read_string(response.text)
            return (
                remote_config.get("Version", "version", fallback="0.0.0"),
                remote_config.get("Version", "update_notes", fallback="更新信息获取失败。")
            )
        except Exception as e:
            print(f'获取远程版本失败: {e}')
            return (None, None)

    def check_for_update(self) -> bool:
        local_version = self.get_local_version()
        remote_version, update_notes = self.get_remote_version()

        if remote_version is None:
            print(f"可手动检查更新: {self.github_url}")
            return False

        if version.parse(remote_version) > version.parse(local_version):
            print(f"\n发现新版本: {remote_version} (当前版本: {local_version})")
            print(f"更新内容: {update_notes}")
            print(f"项目地址: {self.github_url}")
            
            choice = input("\n是否继续运行当前版本？(y继续 / n退出): ").strip().lower()
            if choice == 'y':
                print("继续运行当前版本...\n")
                return True
            else:
                print("已退出，请手动更新后重试。")
                input("按回车键退出...")
                exit()
        else:
            print("当前已是最新版本。\n")
            return True

def on_check_update(config_data: configparser.ConfigParser, config_path: str) -> VersionChecker:
    checker = VersionChecker(config_data, config_path)
    checker.check_for_update()
    return checker

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config_path = "config.ini"
    config.read(config_path, encoding='utf-8')
    checker = on_check_update(config, config_path)