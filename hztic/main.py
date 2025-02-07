from datetime import datetime
from .config import BeisenAPIConfig
from .config import HesiAPIConfig
from hztic.handler.data_service import fetch_and_store_data, update_role_staffs_with_clean
from hztic.utils.database_manager import DatabaseManager
from hztic.utils.logger import Logger

logger = Logger().get_logger()

def main():
    db_manager = DatabaseManager()
    db_manager.initialize_employee_status()
    
    # 配置时间范围
    # start_time = datetime(2023, 10, 23)
    # end_time = datetime(2025, 1, 25)
    
    start_time = datetime(2025, 2, 6)
    end_time = datetime(2025, 2, 7)

    # 获取北森数据并存储
    fetch_and_store_data(BeisenAPIConfig, start_time, end_time)
    logger.debug("数据存储完成.")
    

    # 获取部门负责人信息
    contents = db_manager.get_organization_staff_mapping(path_type="name")
    logger.debug("部门负责人信息获取完成.")
    
    """更新角色--部门负责人信息"""
    result = update_role_staffs_with_clean(
        config= HesiAPIConfig,
        role_id="ID01EjGAFgd2N1:leader",
        contents=contents,
        staff_by="code"
    )
    
    if result:
        logger.debug("角色--组织负责人:员工信息更新成功")
    else:
        logger.error("角色--组织负责人:员工信息更新失败")
        
    """更新角色--经理级以上员工信息"""
    contents = db_manager.get_manager_org_path()
    logger.debug("经理级以上员工信息获取完成.")
    result = update_role_staffs_with_clean(
        config= HesiAPIConfig,
        role_id="ID01EQlDrnHJ8z",
        contents=contents,
        staff_by="code"
    )
    
    if result:
        logger.debug("角色员工信息更新成功")
    else:
        logger.error("角色员工信息更新失败")
    
    logger.info("程序调度完成.")
    
if __name__ == "__main__":
    main()