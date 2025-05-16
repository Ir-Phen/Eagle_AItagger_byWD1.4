from configparser import ConfigParser

# 配置文件类
class Config:
    def __init__(self, global_config_path):
        self.global_config_path = global_config_path
        self.global_config = None

    # 读取配置文件
    def read_config(self, global_config_path):
        global_config = ConfigParser()
        global_config.read(global_config_path, encoding="utf-8")
        return global_config

    # 从配置文件中获取参数
    def get_config_data(self, section, option, default=None):
        try:
            if self.global_config.has_option(section, option):  # 修改这里
                return self.global_config.get(section, option)  # 修改这里
            else:
                return default
        except Exception as e:
            print(f"读取配置参数 [{section}] {option} 时出错: {e}")
            return default

if __name__ == "__main__":
    True