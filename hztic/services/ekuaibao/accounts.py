import os,time,requests
from hztic.utils.token_manager import HesiTokenManager
from hztic.config import download_dir

class Accounts:
    """收付款账户管理"""
    def __init__(self, config):
        self.config = config
        self.token_manager = HesiTokenManager(config)
        self.download_dir = download_dir

    def get_branch_file(self):
        """
        获取网点信息文件下载链接并保存到本地
        :return: 本地文件路径
        """
        access_token = self.token_manager.get_access_token()
        base_url = self.token_manager.get_base_url()
        url = f"{base_url}/api/openapi/v1/banks/getAllBranch"
        params = {"accessToken": access_token}
        response = requests.post(url, params=params)
        if response.status_code == 200:
            data = response.json()
            code = data.get("code")
            msg = data.get("msg")
            download_url = data.get("url")
            if code == "A200" and download_url:
                return self._download_file(download_url, "branch_info.xlsx")
            elif code in {"A200", "A201", "A202", "A203", "A204"}:
                print(f"Status: {msg}. Retrying in 2-5 minutes...")
                time.sleep(120) 
                return self.get_branch_file()
            else:
                raise Exception(f"Failed to fetch branch file link: {msg}")
        else:
            raise Exception(f"Request failed: {response.status_code}, {response.text}")

    def _download_file(self, download_url, file_name):
        """
        下载文件到本地
        :param download_url: 文件下载链接
        :param file_name: 保存的文件名
        :return: 本地文件路径
        """
        response = requests.get(download_url, stream=True)
        if response.status_code == 200:
            file_path = os.path.join(self.download_dir, file_name)
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"File downloaded successfully: {file_path}")
            return file_path
        else:
            raise Exception(f"Failed to download file: {response.status_code}, {response.text}")