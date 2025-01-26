import requests
from hztic.utils.token_manager import HesiTokenManager

class StaffService:
    """员工列表服务"""
    def __init__(self, config):
        self.config = config
        self.token_manager = HesiTokenManager(config)

    def get_staff_list(self, start=0, count=10, active=True, order_by="updateTime", order_by_type="asc"):
        access_token = self.token_manager.get_access_token()
        base_url = self.token_manager.get_base_url()
        url = f"{base_url}/api/openapi/v1.1/staffs"
        params = {
            "accessToken": access_token,
            "start": start,
            "count": count,
            "active": str(active).lower(),
            "orderBy": order_by,
            "orderByType": order_by_type
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()["items"]
        else:
            raise Exception(f"Failed to fetch staff list: {response.text}")