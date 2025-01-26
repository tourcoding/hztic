import os,time,requests
from typing import Dict, List, Optional
from hztic.utils.token_manager import HesiTokenManager
from hztic.config import download_dir
from hztic.utils.logger import Logger

class HesiOpenApi:
    """合思开放平台API"""
    def __init__(self, config):
        self.logger = Logger().get_logger()
        self.config = config
        self.token_manager = HesiTokenManager(config)
        self.access_token = self.token_manager.get_access_token()
        self.base_url = self.token_manager.get_base_url()
        self.download_dir = download_dir
        
    def auth_staff_api_call(self, add_staff: Optional[List[str]] = None, del_staff: Optional[List[str]] = None) -> bool:
        """
        调用 API 接口,激活或停用员工点位授权。
        
        :param add_staff: 需要激活授权的员工工号数组。
        :param del_staff: 需要停用授权的员工工号数组。
        :return: 如果 API 调用成功且返回值为 True,则返回 True;否则返回 False。
        """
        url = f"{self.base_url}/api/openapi/v1/charge/powers/authStaff"
        params = {"accessToken": self.access_token}
        headers = {
            "content-type": "application/json",
            "Accept": "application/json"
        }
        payload = {"type": "code"}

        if add_staff:
            payload["addStaff"] = add_staff
        if del_staff:
            payload["delStaff"] = del_staff

        try:
            response = requests.post(url, params=params, headers=headers, json=payload)
            if response.status_code == 200:
                result = response.json()
                if result.get("value") is True:
                    self.logger.debug("API 调用成功")
                    self.logger.debug(f"API 返回结果: {response.text}")
                    return True
                else:
                    self.logger.warning("API 调用成功,但返回值为 False")
                    return False
            elif response.status_code == 400:
                error_message = response.json().get("message", "未知错误")
                self.logger.error(f"API 调用失败,状态码: 400,错误信息: {error_message},排查建议：请确认 type(员工标识类型)是否为固定值。")
            else:
                self.logger.error(f"API 调用失败,状态码: {response.status_code}")
                self.logger.debug(f"API 返回结果: {response.text}")
            return False
        except Exception as e:
            self.logger.error(f"API 调用发生异常: {e}")
            return False

    def update_role_staffs(
        self,
        role_id: str,
        contents: List[Dict],
        staff_by: str = "code"
    ) -> bool:
        """
        更新角色配置的员工信息。
        
        :param role_id: 角色ID。
        :param contents: 角色配置内容.格式见示例。
        :param staff_by: 员工标识类型.默认为 "code"。 
        :return: 如果 API 调用成功.则返回 True; 否则返回 False。
        """
        url = f"{self.base_url}/api/openapi/v1.1/roledefs/{role_id}/staffs"
        params = {
            "accessToken": self.access_token,
            "staffBy": staff_by
        }
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "contents": contents
        }

        try:
            response = requests.put(url, params=params, headers=headers, json=payload)
            if response.status_code == 204:
                self.logger.debug("API 调用成功")
                return True
            elif response.status_code == 400:
                self.logger.error("API 调用失败.状态码: 400.错误信息: contents参数不能为空")
                self.logger.info("排查建议：请确认 contents 参数是否拼写正确。")
            elif response.status_code == 403:
                self.logger.error("API 调用失败.状态码: 403.错误信息: 没有权限同步此角色")
                self.logger.info("排查建议：请使用 v1.1 版本接口更新手动管理数据来源的角色.V1 不支持.详见更新日志。")
            elif response.status_code == 412:
                error_message = response.json().get("message", "未知错误")
                self.logger.error(f"API 调用失败.状态码: 412.错误信息: {error_message}")
                if "找不到角色" in error_message:
                    self.logger.info("排查建议：请确认 roledefId(角色ID)是否正确或存在。")
                elif "数据错误" in error_message:
                    self.logger.info("排查建议：请确认 path(部门或自定义档案值)是否为完整路径参数.或员工信息是否正确。")
                elif "参数staffs不能为空" in error_message or "参数path不能为空" in error_message:
                    self.logger.info("排查建议：除了普通角色.path(部门或自定义档案值)、staffs(员工集合)不允许传 null。")
            else:
                self.logger.error(f"API 调用失败.状态码: {response.status_code}")
                self.logger.debug(f"API 返回结果: {response.text}")
            return False
        except Exception as e:
            self.logger.error(f"API 调用发生异常: {e}")
            return False
        
    
    def delete_role_staffs(self, role_id: str) -> bool:
        """
        删除角色配置的员工信息。
        
        :param role_id: 角色ID。
        :return: 如果 API 调用成功，则返回 True; 否则返回 False。
        """
        url = f"{self.base_url}/api/openapi/v1.1/roledefs/{role_id}/staffs"
        params = {
            "accessToken": self.access_token
        }

        try:
            response = requests.delete(url, params=params)
            if response.status_code == 204:
                self.logger.debug("API 调用成功")
                return True
            elif response.status_code == 412:
                error_message = response.json().get("message", "未知错误")
                self.logger.error(f"API 调用失败，状态码: 412,错误信息: {error_message}")
                self.logger.info("描述:找不到角色, 排查建议：请确认 roledefId(角色ID)是否正确或存在.")
            else:
                self.logger.error(f"API 调用失败，状态码: {response.status_code}")
                self.logger.debug(f"API 返回结果: {response.text}")
            return False
        except Exception as e:
            self.logger.error(f"API 调用发生异常: {e}")
            return False
    

    def get_branch_file(self, retry_delay: int = 120, max_retries: int = 3) -> Optional[str]:
        """
        获取网点信息文件下载链接并保存到本地。
        
        :param retry_delay: 重试延迟时间(秒).默认为 120 秒。
        :param max_retries: 最大重试次数.默认为 3 次。
        :return: 本地文件路径.如果失败则返回 None。
        """
        url = f"{self.base_url}/api/openapi/v1/banks/getAllBranch"
        params = {"accessToken": self.access_token}

        for attempt in range(max_retries):
            try:
                response = requests.post(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    code = data.get("code")
                    msg = data.get("msg")
                    download_url = data.get("url")

                    if code == "A200" and download_url:
                        return self._download_file(download_url, "branch_info.xlsx")
                    elif code in {"A201", "A202", "A203", "A204"}:
                        self.logger.warning(f"状态: {msg}。将在 {retry_delay} 秒后重试...")
                        time.sleep(retry_delay)
                    else:
                        self.logger.error(f"获取网点信息文件链接失败: {msg}")
                        return None
                else:
                    self.logger.error(f"请求失败: {response.status_code}, {response.text}")
                    return None
            except Exception as e:
                self.logger.error(f"获取网点信息文件链接时发生异常: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    return None

    def _download_file(self, download_url: str, file_name: str) -> Optional[str]:
        """
        下载文件到本地。
        
        :param download_url: 文件下载链接。
        :param file_name: 保存的文件名。
        :return: 本地文件路径.如果失败则返回 None。
        """
        try:
            response = requests.get(download_url, stream=True)
            if response.status_code == 200:
                file_path = os.path.join(self.download_dir, file_name)
                os.makedirs(self.download_dir, exist_ok=True)
                with open(file_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                self.logger.info(f"文件下载成功: {file_path}")
                return file_path
            else:
                self.logger.error(f"文件下载失败: {response.status_code}, {response.text}")
                return None
        except Exception as e:
            self.logger.error(f"文件下载时发生异常: {e}")
            return None