class Config:
    """
    Ragflow-toolkit 全局配置管理。
    """
    def __init__(self):
        self.headers = {}
        self.timeout = 10  # 默认超时（秒）
        self.retry = 3     # 默认重试次数

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

config = Config() 