import os, json, threading, time, requests, sys
from hztic.config import beisen_token_cache_file, beisen_base_url ,hesi_token_cache_file

class BeisenTokenManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(BeisenTokenManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, config):
        self.config = config
        self.token_cache_file = beisen_token_cache_file  # 缓存文件路径
        self.token_data = None
        self.base_url = beisen_base_url
        self._lock = threading.Lock()
        self._load_token()

    def _load_token(self):
        """从缓存文件中加载 token 和 base_url 数据"""
        if os.path.exists(self.token_cache_file):
            with open(self.token_cache_file, "r") as f:
                data = json.load(f)
                self.token_data = data.get("token_data", {})
                self.base_url = data.get("base_url")
        else:
            self.token_data = {}

    def _save_token(self):
        """将 token 和 base_url 数据保存到缓存文件"""
        data = {
            "token_data": self.token_data,
            "base_url": self.base_url,
        }
        with open(self.token_cache_file, "w") as f:
            json.dump(data, f)
    
    def get_base_url(self):
        """获取 base_url,如果不存在则调用接口获取"""
        if not self.base_url:
            print("请在config文件里配置北森base_url信息!!!")
            sys.exit(1)
        return self.base_url

    def get_access_token(self):
        """获取有效的 accessToken,如果过期则重新获取"""
        with self._lock:
            if (not self.token_data) or self._is_token_expired():
                self._authenticate()
            return self.token_data["access_token"]

    def _is_token_expired(self):
        """检查 token 是否已过期"""
        expire_time = self.token_data.get("expireTime", 0)
        return time.time() * 1000 + 7200000 >= expire_time

    def _authenticate(self):
        """调用授权接口"""
        url = f"{self.base_url}/token"
        payload = {
            "grant_type":"client_credentials",
            "app_key": self.config["app_key"],
            "app_secret": self.config["app_secret"]
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            self.token_data = response.json()
            self._save_token()
        else:
            raise Exception(f"Failed to authenticate: {response.text}")
       

class HesiTokenManager:
    """合思token管理器"""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(HesiTokenManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, config):
        self.config = config
        self.token_cache_file = hesi_token_cache_file  # 缓存文件路径
        self.token_data = None
        self.base_url = None
        self._lock = threading.Lock()
        self._load_token()

    def _load_token(self):
        """从缓存文件中加载 token 和 base_url 数据"""
        if os.path.exists(self.token_cache_file):
            with open(self.token_cache_file, "r") as f:
                data = json.load(f)
                self.token_data = data.get("token_data", {})
                self.base_url = data.get("base_url")
        else:
            self.token_data = {}

    def _save_token(self):
        """将 token 和 base_url 数据保存到缓存文件"""
        data = {
            "token_data": self.token_data,
            "base_url": self.base_url,
        }
        with open(self.token_cache_file, "w") as f:
            json.dump(data, f)

    def get_base_url(self):
        """获取 base_url,如果不存在则调用接口获取"""
        if not self.base_url:
            self._fetch_base_url()
        return self.base_url

    def _fetch_base_url(self):
        """调用接口获取 base_url"""
        url = f"https://app.ekuaibao.com/api/openapi/v2/location"
        params = {"corpId": self.config["corp_id"]}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            self.base_url = response.json()["value"]
            self.base_url = self.base_url.rstrip(self.base_url[-1])
            self._save_token()
        else:
            raise Exception(f"Failed to fetch base_url: {response.text}")

    def get_access_token(self):
        """获取有效的 accessToken,如果过期则刷新"""
        with self._lock:
            if (not self.token_data) or self._is_token_expired():
                self._refresh_token()
            return self.token_data["accessToken"]

    def _is_token_expired(self):
        """检查 token 是否已过期"""
        expire_time = self.token_data.get("expireTime", 0)
        return time.time() * 1000 + 7200000 >= expire_time

    def _refresh_token(self):
        """刷新 token 或重新授权"""
        if "refreshToken" in self.token_data:
            self._refresh_authorization()
        else:
            self._authenticate()

    def _refresh_authorization(self):
        """调用刷新授权接口"""
        url = f"{self.get_base_url()}/api/openapi/v2/auth/refreshToken"
        params = {
            "accessToken": self.token_data["accessToken"],
            "refreshToken": self.token_data["refreshToken"],
            "powerCode": "219904"
        }
        
        response = requests.post(url, params=params)
        if response.status_code == 200:
            self.token_data = response.json()["value"]
            self._save_token()
        else:
            raise Exception(f"Failed to refresh token: {response.text}")

    def _authenticate(self):
        """调用授权接口"""
        url = f"{self.get_base_url()}/api/openapi/v1/auth/getAccessToken"
        payload = {
            "appKey": self.config["app_key"],
            "appSecurity": self.config["app_security"]
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            self.token_data = response.json()["value"]
            self._save_token()
        else:
            raise Exception(f"Failed to authenticate: {response.text}")