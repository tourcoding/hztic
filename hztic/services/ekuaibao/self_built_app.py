import requests
from hztic.utils.token_manager import HesiTokenManager

class SelfBuiltApp:
    """自建应用接口"""
    def __init__(self, config):
        self.config = config
        self.token_manager = HesiTokenManager(config)

    def get_self_built_app_list(self, start=0, count=10):
        """获取自建应用列表"""
        access_token = self.token_manager.get_access_token()
        base_url = self.token_manager.get_base_url()
        url = f"{base_url}/api/openapi/v2/datalink/getPlatform"
        
        headers = {
            'content-type': 'application/json'
        }
        params = {
            "accessToken": access_token,
            "start": start,
            "count": count,
        }
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            return response.json()["items"]
        else:
            raise Exception(f"Failed to fetch staff list: {response.text}")
    
    def get_transaction_data(self, platformId):
        """获取某个应用下的所有业务对象"""
        access_token = self.token_manager.get_access_token()
        base_url = self.token_manager.get_base_url()
        url = f"{base_url}/api/openapi/v2/datalink/entity/${platformId}"
        
        headers = {
            'content-type': 'application/json'
        }
        params = {
            "accessToken": access_token,
        }
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            return response.json()["items"]
        else:
            raise Exception(f"Failed to fetch staff list: {response.text}")
    
    def get_instance_list(self, entityId,start=0, count=100,startDate=None, endDate=None, active=False):
        """获取某个应用下的所有业务对象"""
        access_token = self.token_manager.get_access_token()
        base_url = self.token_manager.get_base_url()
        url = f"{base_url}/api/openapi/v2.1/datalink"
        params = {
            "accessToken": access_token,
            "entityId": entityId,
            "start": start,
            "count": count,
            "startDate": startDate,
            "endDate": endDate,
            "active": active
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()["items"]
        else:
            raise Exception(f"Failed to fetch staff list: {response.text}")
        
    def get_instance_describe(self, entityId, ids = [], codes = [], count=100, index= 1):
        """获取业务对象实例信息"""
        # 获取 AccessToken 和 BaseURL
        access_token = self.token_manager.get_access_token()
        base_url = self.token_manager.get_base_url()
        
        # 请求地址
        url = f"{base_url}/api/openapi/v2/extension/DATA_LINK/object/{entityId}/search"
        
        # 请求头和数据
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        params = {
            "accessToken": access_token,
        }
        
        payload = {
            "index": index,
            "count": count,
            "ids": ids,
            "codes": codes
        }
        
        # 发起 POST 请求
        response = requests.post(url, headers=headers, params=params, json=payload)
        if response.status_code == 200:
            return response.json()["items"]
        else:
            raise Exception(f"Failed to fetch approval matrix: {response.text}")