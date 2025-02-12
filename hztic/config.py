"""合思鉴权配置"""
HesiAPIConfig= {
    "app_key": "ed22508e-613b-4e83-84eb-8d48718ac3d2",
    "app_security": "969aafca-6af5-4de4-a88e-e8f73e7892ad",
    "corp_id": "ID01EjGAFgd2N1"
}

"""北森鉴权配置"""
BeisenAPIConfig= {
    "app_key": "6DEAC7AA8D9147BE9045F70CE99E6A5C",
    "app_secret": "04DBD97693D143FCBF64F39457081DC3635D5CA0BF844370A48D6577F0AA3B7D"
}

"""合思token缓存文件"""
hesi_token_cache_file = r"hztic/data/cache/hesi_token_cache.json"

"""北森token缓存文件"""
beisen_base_url = "https://openapi.italent.cn"
beisen_token_cache_file = r"hztic/data/cache/beisen_token_cache.json"

"""下载文件存储路径"""
download_dir = r"hztic/data/download/"

"""数据库配置"""
DB_DIR = r"hztic/data/db/app.db"

"""日志文件存储路径"""
LOG_DIR = r"hztic/data/logs"