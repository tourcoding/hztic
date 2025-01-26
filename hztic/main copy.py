import json
from hztic.config import HesiAPIConfig, BeisenAPIConfig
from hztic.services import Accounts, StaffService,  SelfBuiltApp, BeisenOpenAPI
from hztic.utils.logger import Logger
from datetime import datetime

def setup_logging():
    """设置全局日志配置"""
    # 创建一个全局使用的日志记录器实例
    global_logger = Logger(name="main")
    return global_logger.get_logger()

# 初始化全局日志记录器
logger = setup_logging()

def main():
    """API初始化"""
    staff_service = StaffService(HesiAPIConfig)
    self_built_app = SelfBuiltApp(HesiAPIConfig)
    organization_service = BeisenOpenAPI(BeisenAPIConfig)

    """调用示例"""
    # 8.
    start_time = datetime.strptime('2023-10-15', '%Y-%m-%d')
    end_time = datetime.strptime('2025-01-23', '%Y-%m-%d')
    organization = organization_service.get_organizations_within_time_range(start_time, end_time,incremental = False)
    logger.info(f"组织信息: {organization}")
    
    employees = organization_service.get_employees_within_time_range(start_time, end_time,incremental = False)
    logger.info(f"员工信息: {employees}")
    
    # try:
    #     # 获取员工信息
    #     staffs = organization_service.get_staffs()
        
    #     # 打印员工信息
    #     print("员工信息列表:")
    #     for staff in staffs:
    #         print(staff)

    #     # 记录日志
    #     logger.info(f"审批矩阵: {staffs}")

    # except Exception as e:
    #     logger.error(f"获取员工信息失败: {e}")
    
    # 1:获取员工列表
    try:
        staff_list = staff_service.get_staff_list(
            start=0,
            count=10,
            active=True,
            order_by="updateTime",
            order_by_type="desc"
        )
        for staff in staff_list:
            print(f"Name: {staff['name']}, Departments: {staff['departments']}")
    except Exception as e:
        # logger.error(f"Error: {e}")
        print(f"Error: {e}")
        

    # 3:获取自建应用列表
    try:
        platform_list = self_built_app.get_self_built_app_list(start=0, count=10)
        for platform in platform_list:
            print(f"Name: {platform['name']}, App ID: {platform['id']}")
    except Exception as e:
        # logger.error(f"Error: {e}")
        print(f"Error: {e}")
    
    
    # 4.获取某个应用下的业务对象
    try:
        transaction_data = self_built_app.get_transaction_data(platformId="ID01EOr6VXxIOH")
        with open("hztic/data/cache/transaction_data.json","w") as f:
          json.dump(transaction_data,f)
    except Exception as e:
        # logger.error(f"Error: {e}")
        print(f"Error: {e}")
        
    # 5.获取某个业务对象下的实例列表
    try:
        instance_list = self_built_app.get_instance_list(entityId="a21343f04774aa5c2fc0",active=True)
        with open("hztic/data/cache/instance_list.json","w") as f:
          json.dump(instance_list,f)
    except Exception as e:
        # logger.error(f"Error: {e}")
        print(f"Error: {e}")
    
    # 6.获取业务对象实例信息
    try:
        instance_describe = self_built_app.get_instance_describe(entityId="a21343f04774aa5c2fc0",count=100,index=1)
        with open("hztic/data/cache/instance_describe.json","w") as f:
          json.dump(instance_describe,f)
    except Exception as e:
        # logger.error(f"Error: {e}")
        print(f"Error: {e}")
        
    # 7.下载所有开户网点信息
    accounts = Accounts(HesiAPIConfig)
    try:
        print("下载所有开户网点信息...")
        file_path = accounts.get_branch_file()
        print(f"文件保存路径: {file_path}")
    except Exception as e:
        # logger.error(f"Error: {e}")
        print(f"Error: {e}")

 
if __name__ == "__main__":
    main()