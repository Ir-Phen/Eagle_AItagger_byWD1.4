import configparser
import socket
import webbrowser
import uvicorn
import os

def get_available_port(global_config, min_port=1024, max_port=65535):
    # 获取可用端口
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('', 0))
        port = s.getsockname()[1]
        # 直接操作传入的全局配置对象
        if not global_config.has_section('server'):
            global_config.add_section('server')
        global_config.set('server', 'port', str(port))
        return port
    finally:
        s.close()
        
def start_server(global_config):
    # 获取服务器配置
    host = global_config.get("server", "host")
    port = get_available_port(global_config)

    # 获取模型配置
    device = global_config.get("model", "device")
    wd14_model = global_config.get("model", "wd14_model")
    wd14_threshold = global_config.getfloat("model", "wd14_threshold")
    replace_underscore = global_config.getboolean("model", "replace_underscore")

    # 设置环境变量
    os.environ["DEVICE"] = device
    os.environ["WD14_MODEL"] = wd14_model
    os.environ["WD14_THRESHOLD"] = str(wd14_threshold)
    os.environ["WD14_REPLACE_UNDERSCORE"] = str(replace_underscore).lower()

    # 导入 FastAPI 应用
    from wd14_tagger_api.server import app

    # 添加自定义路由以处理前端未配置的情况
    @app.get("/")
    async def root():
        # 检查前端是否配置
        if not os.path.exists("path/to/frontend/index.html"):  # 替换为实际的前端文件路径
            return {"message": "前端未配置，请检查配置文件或前端路径"}
        return {"message": "服务器已启动，前端已配置"}
    
    
    # 启动 Uvicorn 服务器
    uvicorn.run(app, host=host, port=port)
    # 打开浏览器
    url = f"http://{host}:{port}"
    webbrowser.open(url)
if __name__ == "__main__":
    start_server()