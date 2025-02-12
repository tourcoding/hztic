import requests
import json
from hztic.utils.rate_limiter import BeisenRateLimiter
from hztic.utils.token_manager import BeisenTokenManager
from hztic.utils.logger import Logger
from datetime import timedelta

class BeisenOpenAPI:
    """北森开发平台接口"""
    def __init__(self, config):
        self.config = config
        self.token_manager = BeisenTokenManager(config)
        self.base_url = self.token_manager.get_base_url()
        self.access_token = self.token_manager.get_access_token()
        self.logger = Logger(name=self.__class__.__name__).get_logger()     # 使用单例模式创建日志对象,显式指定日志名称
        self.rate_limiter = BeisenRateLimiter(requests_per_second=100, requests_per_minute=3000)  # 初始化速率限制器

    def _make_request(self, endpoint, method="GET", headers=None, params=None, data=None, json_data=None):
        url = f"{self.base_url}{endpoint}"
        headers = headers or {}
        headers["Authorization"] = f"Bearer {self.access_token}"
        headers["Content-Type"] = "application/json"

        try:
            self.logger.debug(f"Making request to {url} with method {method}")
            self.logger.debug(f"Headers: {headers}")
            self.logger.debug(f"Params: {params}")
            self.logger.debug(f"Data: {data}")
            self.logger.debug(f"JSON Data: {json_data}")

            response = requests.request(method, url, headers=headers, params=params, data=data, json=json_data)
            response.raise_for_status()  # 如果响应状态码不是 200,抛出异常

            self.logger.debug(f"Response status code: {response.status_code}")
            self.logger.debug(f"Response text: {response.text}")  # 记录原始响应文本

            try:
                json_response = response.json()
                self.logger.debug(f"Parsed Response: {json_response}")
                return json_response
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to decode JSON: {e}")
                self.logger.error(f"Response content: {response.text}")
                raise Exception(f"Failed to decode JSON: {e}. Response content: {response.text}")

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            raise Exception(f"Request failed: {e}")


    def get_organizations_within_time_range(self, start_time, end_time, incremental=False):
        """
        获取指定时间范围内的组织单元信息。
        如果是增量获取,则只查询最新的数据；如果是全量获取,则按90天一段进行分段查询。
        
        :param start_time: 查询的起始时间
        :param end_time: 查询的结束时间
        :param incremental: 是否是增量获取 默认False
        
        @return: 组织单元信息列表
        """
        all_organizations = []

        if not incremental and (end_time - start_time).days > 90:
            segment_start = start_time
            while segment_start < end_time:
                segment_end = min(segment_start + timedelta(days=90), end_time)
                print(f"Fetching data from {segment_start} to {segment_end}")
                organizations = self.get_organization_by_time_window(segment_start, segment_end)
                all_organizations.extend(organizations)
                segment_start = segment_end + timedelta(days=1)
        else:
            print(f"Fetching data from {start_time} to {end_time}")
            all_organizations = self.get_organization_by_time_window(start_time, end_time)

        return all_organizations

    def get_organization_by_time_window(self, start_time, end_time):
        """
        获取根据时间窗滚动查询变动的组织单元信息, 默认时间窗口为90天
        
        :param start_time: 查询的起始时间
        :param end_time: 查询的结束时间
        :return: 组织单元信息列表
        """
        all_organizations = []
        scroll_id = None
        
        # Ensure the time window does not exceed 90 days
        if (end_time - start_time).days > 90:
            raise ValueError("Time window exceeds 90 days. Please split the query into smaller segments.")

        while True:
            self.rate_limiter.wait_for_rate_limit()  # 确保遵守速率限制
            
            payload = {
                "timeWindowQueryType": 1,
                "startTime": start_time.isoformat(),
                "stopTime": end_time.isoformat(),
                "capacity": 300,  # 每批次数据量最大300条
                "columns": [
                    "OId",
                    "POIdOrgAdminNameTreePath",
                    "extsuoshugongsizhuti_609792_1697874494",
                    "PersonInCharge"
                ],
                "extQueries": [],
                "isWithDeleted": False,
                "enableTranslate": True,
                "sort": {"Name": 1},
                "scrollId": scroll_id
            }

            try:
                response = self._make_request("/TenantBaseExternal/api/v5/Organization/GetByTimeWindow", method="POST", data=json.dumps(payload))

                # 如果 _make_request 返回 None,则直接跳过此次循环
                if response is None:
                    self.logger.error("API request failed and returned None.")
                    break

                # 检查响应的状态码
                if not isinstance(response, dict) or "code" not in response:
                    self.logger.error("Invalid response format from API.")
                    break

                if response["code"] != '200':
                    self.logger.error(f"API returned an error: {response.get('message', 'Unknown error')}")
                    break  # 调用接口失败,需要记录错误日志信息便于后续排查

                scroll_id = response.get("scrollId")

                if not response.get("data"):
                    # 数据为空表示获取完毕
                    break

                organizations = self._extract_organizations(response["data"])
                all_organizations.extend(organizations)

                # 滚动查询有过期时间限制,确保在10秒内完成下一次请求
                if not organizations:
                    break

            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to decode JSON: {e}")
                raise Exception(f"Failed to decode JSON: {e}. Response content was not a valid JSON.")
            
            except Exception as e:
                self.logger.error(f"Failed to fetch organization data: {e}")
                break  # 发生异常时停止循环

        return all_organizations

    def _extract_organizations(self, org_data_list):
        """从响应数据中提取组织信息"""
        organizations = []
        for org_data in org_data_list:
            translate_properties = org_data.get("translateProperties", {})
            custom_properties = org_data.get("customProperties", {})
            
            # 确保 custom_properties 是一个字典,如果不是,则初始化为空字典,避免为Null时使用get()方法构造信息字典出现Error
            if not isinstance(custom_properties, dict):
                custom_properties = {}
            
            # 确保 translate_properties 是一个字典,如果不是,则初始化为空字典
            if not isinstance(translate_properties, dict):
                translate_properties = {}
                
            # 构造每个组织的信息字典
            organization_info = {
                "organization_id": org_data.get("oId"),
                "name": translate_properties.get("extsuoshugongsizhuti_609792_1697874494Text"),  # 组织名称
                "person_in_charge_id": org_data.get("personInCharge"),  # 负责人ID
                "person_in_charge_text": translate_properties.get("PersonInChargeText"),  # 负责人显示文本
                "tree_path": translate_properties.get("POIdOrgAdminNameTreePathText"),  # 组织树路径
                # "created_time": org_data.get("createdTime"),
                # "modified_time": org_data.get("modifiedTime"),
                "custom_property": custom_properties.get("extsuoshugongsizhuti_609792_1697874494"),  # 自定义属性
            }
            organizations.append(organization_info)
        return organizations


    def get_staffs(self):
        """根据员工ID获取员工信息"""
        self.logger.info("Fetching staffs...")
        endpoint = "/UserFrameworkApiV3/api/v1/staffs/Get"
        
        params = {
            "userId": '614507242',  # 这里假设只需要一个字符串作为参数
        }

        try:
            response = self._make_request(endpoint, method="GET", params=params)
            
            # 检查响应是否包含必要的键
            if not all(key in response for key in ["total", "code", "message", "items"]):
                self.logger.error("Unexpected response structure from the server.")
                raise Exception("Unexpected response structure from the server.")

            # 检查响应的状态码
            if response["code"] != 200:
                self.logger.error(f"API returned an error: {response.get('message', 'Unknown error')}")
                raise Exception(f"API returned an error: {response.get('message', 'Unknown error')}")

            # 检查是否有员工数据
            if response["total"] == 0 or not response["items"]:
                self.logger.warning("No staff data found.")
                return []

            # 提取并返回员工信息
            staff_items = response["items"]
            staff_list = []
            for item in staff_items:
                staff_dto = item.get("staffDto", {})
                department_dto = item.get("departmentDto", {})
                position_dto = item.get("positionDto", {})
                reportings = item.get("reportings", [])

                # 根据需要构造返回的数据结构
                staff_info = {
                    "name": staff_dto.get("name"),
                    "staffCode": staff_dto.get("staffCode"),
                    "email": staff_dto.get("email"),
                    "department": department_dto.get("name"),
                    "position": position_dto.get("name"),
                    "lineManager": next((r for r in reportings if r.get("reportingType") == "直线经理"), {}).get("name"),
                    "userId": staff_dto.get("userId"),
                    # 添加其他你需要的字段...
                }
                staff_list.append(staff_info)

            return staff_list

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON: {e}")
            raise Exception(f"Failed to decode JSON: {e}. Response content: {response.text}")

        except Exception as e:
            self.logger.error(f"Failed to fetch staffs: {e}")
            raise  # 再次抛出异常以允许调用方处理
        
    
    def get_employees_within_time_range(self, start_time, end_time, incremental=False):
        """
        获取一段时间内发生变化的员工信息与单条任职记录数据
        如果是增量获取,则只查询最新的数据；如果是全量获取,则按90天一段进行分段查询。
        
        :param start_time: 查询的起始时间
        :param end_time: 查询的结束时间
        :param incremental: 是否是增量获取 默认False
        
        @return: 组织单元信息列表
        """
        all_employees = []

        if not incremental and (end_time - start_time).days > 90:
            segment_start = start_time
            while segment_start < end_time:
                segment_end = min(segment_start + timedelta(days=90), end_time)
                print(f"Fetching data from {segment_start} to {segment_end}")
                employees = self.get_employees_by_time_window(segment_start, segment_end)
                all_employees.extend(employees)
                segment_start = segment_end + timedelta(days=1)
        else:
            print(f"Fetching data from {start_time} to {end_time}")
            employees = self.get_employees_by_time_window(start_time, end_time)

        return all_employees
    
    
    def get_employees_by_time_window(self, start_time, end_time):
        """
        获取一段时间内发生变化的员工信息与单条任职记录数据, 默认时间窗口为90天
        
        :param start_time: 查询的起始时间
        :param end_time: 查询的结束时间
        :return: 组织单元信息列表
        """
        all_employees = []
        scroll_id = None
        
        # Ensure the time window does not exceed 90 days
        if (end_time - start_time).days > 90:
            raise ValueError("Time window exceeds 90 days. Please split the query into smaller segments.")

        while True:
            self.rate_limiter.wait_for_rate_limit()  # 确保遵守速率限制
            
            payload = {
                "empStatus": [2,3],
                "employType": [0],          # 0 内部员工  1 外部人员  2 实习生
                "serviceType": [0,1],       # 0 主职  1 兼职
                "timeWindowQueryType": 1,   # 时间窗查询类型
                "startTime": start_time.isoformat(), #时间范围开始时间
                "stopTime": end_time.isoformat(),    #时间范围结束时间
                "capacity": 300,                     #每批次数目
                "columns": ["Name","EmployType","extyinhangg_609792_2118474221","extkaihuhangzhihang_609792_463003869","extyinhangzhanghao_609792_395264758","IDNumber","JobNumber","OIdDepartment","serviceType","OIdJobLevel"],
                "extQueries": [                      #自定义字段查询条件
                    {
                        "fieldName": "OIdJobLevel",
                        "queryType": 5,              #等于
                        "values": [
                            "c28789f8-4e66-4365-84a3-b84a1f49d5c7","18eb7a69-e31a-4e9d-b44e-ef75c451b2cf"
                        ]
                    }
                ],
                
                "isWithDeleted": False,
                "enableTranslate": True,
                "sort": {"Name":1},
                "scrollId": scroll_id
            }

            try:
                response = self._make_request("/TenantBaseExternal/api/v5/Employee/GetByTimeWindow", method="POST", data=json.dumps(payload))

                # 如果 _make_request 返回 None,则直接跳过此次循环
                if response is None:
                    self.logger.error("API request failed and returned None.")
                    break

                # 检查响应的状态码
                if not isinstance(response, dict) or "code" not in response:
                    self.logger.error("Invalid response format from API.")
                    break

                if response["code"] != '200':
                    self.logger.error(f"API returned an error: {response.get('message', 'Unknown error')}")
                    break  # 调用接口失败,需要记录错误日志信息便于后续排查

                scroll_id = response.get("scrollId")

                if not response.get("data"):
                    # 数据为空表示获取完毕
                    break

                employees = self._extract_employees(response["data"])
                all_employees.extend(employees)

                # 滚动查询有过期时间限制,确保在10秒内完成下一次请求
                if not employees:
                    break
            
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to decode JSON: {e}")
                raise Exception(f"Failed to decode JSON: {e}. Response content was not a valid JSON.")
            
            except Exception as e:
                self.logger.error(f"Failed to fetch organization data: {e}")
                break  # 发生异常时停止循环
        
        return all_employees
    
    
    def _extract_employees(self, emp_data_list):
        """从响应数据中提取员工任职信息"""
        employees = []
        for emp_data in emp_data_list:
            record_info = emp_data.get("recordInfo", {})
            employee_info = emp_data.get("employeeInfo", {})
            
            # 确保 custom_properties 是一个字典,如果不是,则初始化为空字典,避免为Null时使用get()方法构造信息字典出现Error
            if not isinstance(record_info, dict):
                record_info = {}
            
            # 确保 translate_properties 是一个字典,如果不是,则初始化为空字典
            if not isinstance(employee_info, dict):
               employee_info = {}
            
            # 构造每个员工任职的信息字典
            appointment_info = {
                "job_number": record_info.get("jobNumber"),  # 工号
                "employee_info": employee_info.get("name"),  # 自定义属性
            }
            employees.append(appointment_info)
            
        return employees