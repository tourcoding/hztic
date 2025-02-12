from datetime import datetime
from typing import Dict, List
from hztic.services.beisen import BeisenOpenAPI
from hztic.services.hesi import HesiOpenApi
from hztic.utils.database_manager import DatabaseManager
from hztic.utils.logger import Logger

logger = Logger().get_logger()

def fetch_and_store_data(config: Dict, start_time: datetime, end_time: datetime):
    """从北森开放平台获取数据并存储到数据库中"""
    api = BeisenOpenAPI(config)
    db_manager = DatabaseManager()
    
    corporations = api.get_corporation_within_time_range(start_time, end_time)
    for corporation in corporations:
        db_manager.save_corporation(corporation)
    logger.info("corporation data fetched.")
    
    job_levels = api.get_job_level_within_time_range(start_time, end_time)
    for job_level in job_levels:
        db_manager.save_job_level(job_level)
    logger.info("job level data fetched.")
        
    employment_forms = api.get_employment_form_within_time_range(start_time, end_time)
    for employment_form in employment_forms:
        db_manager.save_employment_form(employment_form)
    logger.info("employment form data fetched.")

    organizations = api.get_organizations_within_time_range(start_time, end_time)
    for org in organizations:
        db_manager.save_organization(org)
    logger.info("organization data fetched.")

    employees = api.get_employees_within_time_range(start_time, end_time)
    for emp in employees:
        db_manager.save_employee(emp)
    logger.info("employee data fetched.")
    

def update_role_staffs_with_clean(
    config: Dict,
    role_id: str,
    contents: List[Dict],
    staff_by: str = "code"
) -> bool:
    """
    更新角色配置的员工信息，调用前先删除角色配置的员工信息。
    
    :param role_id: 角色ID。
    :param contents: 角色配置内容，格式见示例。
    :param staff_by: 员工标识类型，默认为 "code"。
    :return: 如果 API 调用成功，则返回 True；否则返回 False。
    """
    api = HesiOpenApi(config)
    
    # 1. 激活员工账号
    logger.info(f"开始激活员工账号...")
    # 从 contents 中提取所有工号
    staff_codes = []
    for item in contents:
        if "staffs" in item:  # 确保 staffs 字段存在
            staff_codes.extend(item["staffs"])  # 将工号添加到列表中

    # 调用 API 函数
    if not api.auth_staff_api_call(add_staff=staff_codes):
        logger.error("激活员工账号失败，终止更新操作")
        return False

    # 2. 先删除角色配置的员工信息
    logger.info(f"开始删除角色 {role_id} 的员工信息...")
    if not api.delete_role_staffs(role_id):
        api.logger.error(f"删除角色 {role_id} 的员工信息失败，终止更新操作")
        return False
    
    # 3. 删除成功后，更新角色配置的员工信息
    logger.info(f"开始更新角色 {role_id} 的员工信息...")
    if not api.update_role_staffs(role_id, contents, staff_by):
        logger.error(f"更新角色 {role_id} 的员工信息失败")
        return False

    logger.info(f"角色 {role_id} 的员工信息更新成功")
    return True
