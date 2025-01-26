"""Defines the Beisen OpenAPI class."""
import requests
import json
from datetime import timedelta
from typing import Dict, List, Optional, Any
from hztic.utils.rate_limiter import BeisenRateLimiter
from hztic.utils.token_manager import BeisenTokenManager
from hztic.utils.logger import Logger
from hztic.models.base_models import Organization, Employee, JobLevel, EmploymentForm, Corporation

API_SUCCESS_CODE = "200"
DEFAULT_TIME_WINDOW_DAYS = 90
DEFAULT_CAPACITY = 300

class BeisenOpenAPI:
    """北森开放平台API类"""
    def __init__(self, config: Dict):
        self.logger = Logger(name=self.__class__.__name__).get_logger()
        self.config = config
        self.token_manager = BeisenTokenManager(config)
        self.base_url = self.token_manager.get_base_url()
        self.access_token = self.token_manager.get_access_token()
        self.rate_limiter = BeisenRateLimiter(requests_per_second=100, requests_per_minute=3000)

    def _make_request(self, endpoint: str, method: str = "GET", **kwargs) -> Optional[Dict]:
        """
        北森开放平台API的通用请求方法包装器。

        :param endpoint: API端点。
        :param method: HTTP请求方法, 默认为GET。
        :param kwargs: 其他请求参数。
        :return: 响应中的JSON数据, 如果请求失败则返回None。
        """
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.get("headers", {})
        headers.update({
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        })

        try:
            response = requests.request(method, url, headers=headers, **kwargs)
            self.logger.debug(f"Response status code: {response.status_code}") 
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            raise Exception(f"Request failed: {e}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON: {e}", extra={"response_content": response.text})
            raise Exception(f"Failed to decode JSON: {e}. Response content: {response.text}")

    def _fetch_data_in_segments(self, start_time, end_time, incremental: bool, fetch_func):
        """
        分段获取数据。

        :param start_time: 数据检索的开始时间。
        :param end_time: 数据检索的结束时间。
        :param incremental: 是否增量获取数据。
        :param fetch_func: 数据获取函数。
        :return: 获取到的数据列表。
        """
        if not incremental and (end_time - start_time).days > DEFAULT_TIME_WINDOW_DAYS:
            all_data = []
            segment_start = start_time
            while segment_start < end_time:
                segment_end = min(segment_start + timedelta(days=DEFAULT_TIME_WINDOW_DAYS), end_time)
                self.logger.debug(f"Fetching data from {segment_start} to {segment_end}")
                data = fetch_func(segment_start, segment_end)
                all_data.extend(data)
                segment_start = segment_end + timedelta(days=1)
            return all_data
        else:
            self.logger.debug(f"Fetching data from {start_time} to {end_time}")
            return fetch_func(start_time, end_time)

    def _scroll_fetch(self, endpoint: str, payload: Dict, extract_func) -> List[Any]:
        """
        分页查询的通用方法。

        :param endpoint: API端点。
        :param payload: 请求负载。
        :param extract_func: 数据提取函数。
        :return: 提取的数据列表。
        """
        all_data = []
        scroll_id = None

        while True:
            self.rate_limiter.wait_for_rate_limit()
            payload["scrollId"] = scroll_id

            response = self._make_request(endpoint, method="POST", json=payload)
            if not response or response.get("code") != API_SUCCESS_CODE:
                self.logger.error("API request failed or returned an error.")
                break

            scroll_id = response.get("scrollId")
            if not response.get("data"):
                break

            data = extract_func(response["data"])
            all_data.extend(data)

            if not data:
                break

        return all_data

    def get_organizations_within_time_range(self, start_time, end_time, incremental: bool = False) -> List[Organization]:
        """
        Fetch organizational unit information within the specified time range.

        :param start_time: Start time of the time range.
        :param end_time: End time of the time range.
        :param incremental: Whether to fetch data incrementally, defaults to False.
        :return: List of extracted organizational unit information.
        """
        return self._fetch_data_in_segments(start_time, end_time, incremental, self.get_organization_by_time_window)

    def get_organization_by_time_window(self, start_time, end_time) -> List[Organization]:
        """
        Fetch organizational unit information based on time window.

        :param start_time: Start time of the time window.
        :param end_time: End time of the time window.
        :return: List of extracted organizational unit information.
        """
        if (end_time - start_time).days > DEFAULT_TIME_WINDOW_DAYS:
            raise ValueError(f"Time window exceeds {DEFAULT_TIME_WINDOW_DAYS} days. Please split the query into smaller segments.")

        payload = {
            "timeWindowQueryType": 1,
            "startTime": start_time.isoformat(),
            "stopTime": end_time.isoformat(),
            "capacity": DEFAULT_CAPACITY,
            "columns": ["OId", "POIdOrgAdminNameTreePath", "extsuoshugongsizhuti_609792_1697874494", "PersonInCharge","Name"],
            "extQueries": [],
            "isWithDeleted": False,
            "enableTranslate": True,
            "sort": {"Name": 1}
        }

        return self._scroll_fetch("/TenantBaseExternal/api/v5/Organization/GetByTimeWindow", payload, self._extract_organizations)

    def _extract_organizations(self, org_data_list: List[Dict]) -> List[Organization]:
        """
        Extract organization information from response data.

        Iterate through the org_data_list, creating an Organization object for each dictionary.
        Use the get method to retrieve values from the dictionary to avoid exceptions when keys are missing.
        For nested attributes, use chained get methods with the or operator to provide a default value of {} and avoid KeyError.
        """
        return [
            Organization(
                org_id=org_data.get("oId"),
                org_name=org_data.get("name"),
                person_in_charge=org_data.get("personInCharge"),
                person_in_charge_text=(org_data.get("translateProperties") or {}).get("PersonInChargeText"),
                tree_path=org_data.get("pOIdOrgAdminNameTreePath"),
                tree_path_text=(org_data.get("translateProperties") or {}).get("POIdOrgAdminNameTreePathText"),
                extsuoshugongsizhuti=(org_data.get("customProperties") or {}).get("extsuoshugongsizhuti_609792_1697874494"),
                extsuoshugongsizhuti_text=(org_data.get("translateProperties") or {}).get("extsuoshugongsizhuti_609792_1697874494Text"),
            )
            for org_data in org_data_list
        ]

    def get_employees_within_time_range(self, start_time, end_time, incremental: bool = False) -> List[Employee]:
        return self._fetch_data_in_segments(start_time, end_time, incremental, self.get_employees_by_time_window)

    def get_employees_by_time_window(self, start_time, end_time) -> List[Employee]:
        if (end_time - start_time).days > DEFAULT_TIME_WINDOW_DAYS:
            raise ValueError(f"Time window exceeds {DEFAULT_TIME_WINDOW_DAYS} days. Please split the query into smaller segments.")

        payload = {
            "empStatus": [2, 3, 6, 8],             # 1:待入职，2:试用，3:正式，4:调出，5:待调入，6:退休，8:离职，12:非正式
            "employType": [0,1,2],                 # 0:正式员工，1:外部人员，2:实习员工  
            "serviceType": [0],                 # 0:主职，1:兼职
            "timeWindowQueryType": 1,
            "startTime": start_time.isoformat(),
            "stopTime": end_time.isoformat(),
            "capacity": DEFAULT_CAPACITY,
            "columns": ["Name", "EmployType", "extyinhangg_609792_2118474221", "extkaihuhangzhihang_609792_463003869", "extyinhangzhanghao_609792_395264758", "JobNumber", "OIdDepartment", "serviceType", "OIdJobLevel","MobilePhone","iDNumber","EmployeeStatus","email","EmploymentForm"],
            "extQueries": [{
                # "fieldName": "OIdJobLevel",
                # "queryType": 5,
                # "values": ["c28789f8-4e66-4365-84a3-b84a1f49d5c7", "18eb7a69-e31a-4e9d-b44e-ef75c451b2cf"]
            }],
            "isWithDeleted": False,
            "enableTranslate": True,
            "sort": {"Name": 1}
        }

        return self._scroll_fetch("/TenantBaseExternal/api/v5/Employee/GetByTimeWindow", payload, self._extract_employees)

    def _extract_employees(self, emp_data_list: List[Dict]) -> List[Employee]:
        return [
            Employee(
                user_id=(emp_data.get("employeeInfo") or {}).get("userID"),
                employee_name=(emp_data.get("employeeInfo") or {}).get("name"),
                job_number=(emp_data.get("recordInfo") or {}).get("jobNumber"),
                email=(emp_data.get("employeeInfo") or {}).get("email"),
                id_number=(emp_data.get("employeeInfo") or {}).get("iDNumber"),
                mobile_phone=(emp_data.get("employeeInfo") or {}).get("mobilePhone"),
                oId_department_id=(emp_data.get("recordInfo") or {}).get("oIdDepartment"),
                oId_job_level_id=(emp_data.get("recordInfo") or {}).get("oIdJobLevel"),
                employee_status = (emp_data.get("recordInfo") or {}).get("employeeStatus"),
                employment_form = (emp_data.get("recordInfo") or {}).get("employmentForm"),
                service_type = (emp_data.get("recordInfo") or {}).get("serviceType"),
                oId_job_level_text=((emp_data.get("recordInfo") or {}).get("translateProperties") or {}).get("OIdJobLevelText"),
                oId_department_text=((emp_data.get("recordInfo") or {}).get("translateProperties") or {}).get("OIdDepartmentText")
            )
            for emp_data in emp_data_list
        ]
        
        
    def get_job_level_within_time_range(self, start_time, end_time, incremental: bool = False) -> List[JobLevel]:
        return self._fetch_data_in_segments(start_time, end_time, incremental, self.get_job_level_by_time_window)
    
    def get_job_level_by_time_window(self, start_time, end_time) -> List[JobLevel]:
        if (end_time - start_time).days > DEFAULT_TIME_WINDOW_DAYS:
            raise ValueError(f"Time window exceeds {DEFAULT_TIME_WINDOW_DAYS} days. Please split the query into smaller segments.")

        payload = {
            "timeWindowQueryType": 1,
            "startTime": start_time.isoformat(),
            "stopTime": end_time.isoformat(),
            "capacity": DEFAULT_CAPACITY,
            "columns": ["Name","OId","StartDate","Level"],
            "extQueries": [],
            "enableTranslate": True,
            "sort": {"Name": 1}
        }

        return self._scroll_fetch("/TenantBaseExternal/api/v5/JobLevel/GetByTimeWindow", payload, self._extract_job_level)

    def _extract_job_level(self, job_level_data_list: List[Dict]) -> List[JobLevel]:
        return [
            JobLevel(
                name=job_level_data.get("name"),
                object_id=job_level_data.get("objectId")
            )
            for job_level_data in job_level_data_list
        ]
        
        
    def get_employment_form_within_time_range(self, start_time, end_time, incremental: bool = False) -> List[EmploymentForm]:
        return self._fetch_data_in_segments(start_time, end_time, incremental, self.get_employment_form_by_time_window)
    
    def get_employment_form_by_time_window(self, start_time, end_time) -> List[EmploymentForm]:
        """
        Fetch employment form information based on time window.

        :param start_time: Start time of the time window.
        :param end_time: End time of the time window.
        :return: List of extracted employment form information.
        """
        if (end_time - start_time).days > DEFAULT_TIME_WINDOW_DAYS:
            raise ValueError(f"Time window exceeds {DEFAULT_TIME_WINDOW_DAYS} days. Please split the query into smaller segments.")

        payload = {
            "timeWindowQueryType": 1,
            "startTime": start_time.isoformat(),
            "stopTime": end_time.isoformat(),
            "capacity": DEFAULT_CAPACITY,
            "columns":["Name","StartDate"],
            "enableTranslate": True,
            "sort": {"Name": 1}
        }

        return self._scroll_fetch("/TenantBaseExternal/api/v5/EmploymentForm/GetByTimeWindow", payload, self._extract_employment_form)

    def _extract_employment_form(self, employment_form_data_list: List[Dict]) -> List[EmploymentForm]:
        """
        Extract employment form information from response data.

        :param employment_form_data_list: List containing employment form data.
        :return: List of extracted employment form information.
        """
        return [
            EmploymentForm(
                name=employment_form_data.get("name"),
                object_id=employment_form_data.get("objectId")
            )
            for employment_form_data in employment_form_data_list
        ]
        
        
    def get_corporation_within_time_range(self, start_time, end_time, incremental: bool = False) -> List[Corporation]:
        """
        Fetch company information based on time range.

        :param start_time: Start time of the time range.
        :param end_time: End time of the time range.
        :param incremental: Whether to fetch data incrementally, defaults to False.
        :return: List of extracted company information.
        """
        return self._fetch_data_in_segments(start_time, end_time, incremental, self.get_corporation_by_time_window)
    
    def get_corporation_by_time_window(self, start_time, end_time) -> List[Corporation]:
        """
        Fetch company information based on time window.

        :param start_time: Start time of the time window.
        :param end_time: End time of the time window.
        :return: List of extracted company information.
        """
        if (end_time - start_time).days > DEFAULT_TIME_WINDOW_DAYS:
            raise ValueError(f"Time window exceeds {DEFAULT_TIME_WINDOW_DAYS} days. Please split the query into smaller segments.")

        payload = {
            "metaObjectName": "Corporation",
            "timeWindowQueryType": 1,
            "startTime": start_time.isoformat(),
            "stopTime": end_time.isoformat(),
            "capacity": DEFAULT_CAPACITY,
            "columns":["OId","Name","extzuzhidaima_609792_945002890","extkaihuyinhang_609792_103657435","extyinhangzhanghao_609792_990841835","extdianhua_609792_1936418435","extdengjidizhi_609792_1284935992","Status"],
            "enableTranslate": True,
            "sort": {"Name": 1}
        }

        return self._scroll_fetch("/TenantBaseExternal/api/v5/CommonMetaObject/GetByTimeWindow", payload, self._extract_corporation)


    def _extract_corporation(self, corporation_data_list: List[Dict]) -> List[Corporation]:
        """
        Extract company information from response data.

        :param corporation_data_list: List containing company data.
        :return: List of extracted company information.
        """
        return [
            Corporation(
                corp_id=(corp_data.get("fields") or {}).get("OId"),
                corp_name=(corp_data.get("fields") or {}).get("Name"),
                extzuzhidaima=(corp_data.get("fields") or {}).get("extzuzhidaima_609792_945002890"),
                extkaihuyinhang = (corp_data.get("fields") or {}).get("extkaihuyinhang_609792_103657435"),
                extyinhangzhanghao = (corp_data.get("fields") or {}).get("extyinhangzhanghao_609792_990841835"),
                extdengjidizhi = (corp_data.get("fields") or {}).get("extdengjidizhi_609792_1284935992"),
                extdianhua = (corp_data.get("fields") or {}).get("extdianhua_609792_1936418435")
            )
            
            for corp_data in corporation_data_list
        ]