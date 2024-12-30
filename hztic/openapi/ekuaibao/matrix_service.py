import requests
from hztic.utils.HesiTokenManger import HesiTokenManager

class MatrixService:
    """企业审批矩阵服务"""
    def __init__(self, config):
        self.config = config
        self.token_manager = HesiTokenManager(config)

    def get_approval_matrix(self, start=0, count=10):
        """获取企业所有审批矩阵"""
        # 获取 AccessToken 和 BaseURL
        access_token = self.token_manager.get_access_token()
        base_url = self.token_manager.get_base_url()
        
        # 请求地址
        url = f"{base_url}/api/openapi/v2/matrix/search"
        
        # 请求头和数据
        headers = {
            "Content-Type": "application/json",
        }
        params = {
            "accessToken": access_token,
        }
        payload = {
            "limit": {
                "start": start,
                "count": count
            }
        }
        
        # 发起 POST 请求
        response = requests.post(url, headers=headers, params=params, json=payload)
        if response.status_code == 200:
            return response.json()["items"]
        else:
            raise Exception(f"Failed to fetch approval matrix: {response.text}")