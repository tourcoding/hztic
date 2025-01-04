import requests,json
from hztic.utils.BeisenTokenManager import HesiTokenManager

class OrganizationService:
    """企业审批矩阵服务"""
    def __init__(self, config):
        self.config = config
        self.token_manager = HesiTokenManager(config)

    def get_organization(self):
        """获取根据时间窗滚动查询变动的组织单元信息"""
        # 获取 AccessToken 和 BaseURL
        access_token = self.token_manager.get_access_token()
        base_url = self.token_manager.get_base_url()
        
        # 请求地址
        url = f"{base_url}/TenantBaseExternal/api/v5/Organization/GetByTimeWindow"
        
        # 请求头和数据
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        params = json.dumps({
            "timeWindowQueryType": 1,
            "startTime": "2024-12-01",
            "stopTime": "2024-12-05",
            "capacity": 100,
            "columns": [
                "OId",
                "POIdOrgAdminNameTreePath",
                "extsuoshugongsizhuti_609792_1697874494",
                "PersonInCharge"
            ],
            "extQueries": [],
            "isWithDeleted": False,
            "enableTranslate": True,
            "sort": {
                "Name": 1
            },
            "scrollId": ""
        })
        
        # 发起 POST 请求
        response = requests.post(url, headers=headers, data=params)
        if response.status_code == 200:
            print(response.json())
            return response.json()
        else:
            raise Exception(f"Failed to fetch approval matrix: {response.text}")