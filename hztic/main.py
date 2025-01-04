import json
from hztic.config import HesiAPIConfig, BeisenAPIConfig
from hztic.openapi import Accounts, StaffService, MatrixService, SelfBuiltApp, OrganizationService

def main():
    """API初始化"""
    staff_service = StaffService(HesiAPIConfig)
    matrix_service = MatrixService(HesiAPIConfig)
    self_built_app = SelfBuiltApp(HesiAPIConfig)
    organization_service = OrganizationService(BeisenAPIConfig)

    """调用示例"""
    # 8.
    organization = organization_service.get_organization()
    print(organization)
    
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
        print(f"Error: {e}")
        
    # 2:获取审批矩阵
    try:
        approval_matrix = matrix_service.get_approval_matrix(start=0, count=10)
        print(f"Approval Matrix: {approval_matrix}")
    except Exception as e:
        print(f"Error: {e}")

    # 3:获取自建应用列表
    try:
        platform_list = self_built_app.get_self_built_app_list(start=0, count=10)
        for platform in platform_list:
            print(f"Name: {platform['name']}, App ID: {platform['id']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 4.获取某个应用下的业务对象
    try:
        transaction_data = self_built_app.get_transaction_data(platformId="ID01EOr6VXxIOH")
        with open("hztic/config/cache/transaction_data.json","w") as f:
          json.dump(transaction_data,f)
          print("获取某个应用下的业务对象完成...")
    except Exception as e:
        print(f"Error: {e}")
        
    # 5.获取某个业务对象下的实例列表
    try:
        instance_list = self_built_app.get_instance_list(entityId="a21343f04774aa5c2fc0",active=True)
        with open("hztic/config/cache/instance_list.json","w") as f:
          json.dump(instance_list,f)
          print("获取某个业务对象下的实例列表完成...")
    except Exception as e:
        print(f"Error: {e}")
    
    # 6.获取业务对象实例信息
    try:
        instance_describe = self_built_app.get_instance_describe(entityId="a21343f04774aa5c2fc0",count=100,index=1)
        with open("hztic/config/cache/instance_describe.json","w") as f:
          json.dump(instance_describe,f)
          print("获取业务对象实例信息完成...")
    except Exception as e:
        print(f"Error: {e}")
        
    # 7.下载所有开户网点信息
    accounts = Accounts(HesiAPIConfig)
    try:
        print("下载所有开户网点信息...")
        file_path = accounts.get_branch_file()
        print(f"开户网点信息保存到: {file_path}")
    except Exception as e:
        print(f"Error: {e}")

 
if __name__ == "__main__":
    main()