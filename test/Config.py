from configparser import ConfigParser

# 配置文件类
class Config:
    @staticmethod
    def __init__(self):
        self.global_config_path = None
        self.global_config = None

    # 读取配置文件
    @staticmethod
    def read_config(global_config_path):
        global_config = ConfigParser()
        global_config.read(global_config_path, encoding="utf-8")
        return global_config

    # 从配置文件中获取参数
    @staticmethod
    def get_config_data(global_config, section, option, default=None):
        try:
            if global_config.has_option(section, option):
                return global_config.get(section, option)
            else:
                return default
        except Exception as e:
            print(f"读取配置参数 [{section}] {option} 时出错: {e}")
            return default
  

if __name__ == "__main__":
    Config