class HesiAPIConfig:
    """鉴权配置"""
    def __init__(self, app_key, app_security, corp_id):
        self.app_key = app_key
        self.app_security = app_security
        self.corp_id = corp_id
        
 
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "123456",
    "database": "test",
    "charset": "utf8mb4"
}

"""合思token缓存文件"""
hesi_token_cache_file = r"hztic/config/cache/hesi_token_cache.json"

"""北森token缓存文件"""
beisen_token_cache_file = r"hztic/config/cache/beisen_token_cache.json"

"""下载文件存储路径"""
download_dir = r"hztic/config/download/"