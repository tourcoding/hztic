"""
主程序模块

该模块提供了定时任务调度功能,用于同步和更新组织架构数据。

主要功能:
- 定时从北森系统获取组织架构数据并存储到本地数据库
- 更新合思系统中的角色-员工对应关系
- 支持命令行参数控制立即执行任务
"""

from datetime import datetime, timedelta
import argparse
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from .config import BeisenAPIConfig
from .config import HesiAPIConfig
from hztic.handler.data_service import fetch_and_store_data, update_role_staffs_with_clean
from hztic.utils.database_manager import DatabaseManager
from hztic.utils.logger import Logger

logger = Logger().get_logger()

def job():
    """每日执行的任务"""
    try:
        db_manager = DatabaseManager()
        db_manager.initialize_employee_status()
        
        # 配置时间范围 - 获取最近一周的数据
        end_time = (datetime.now() + timedelta(days=0)).replace(hour=0, minute=0, second=0, microsecond=0)  # 获取当前日期
        start_time = end_time - timedelta(days=7)

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
            logger.debug("角色--经理级以上员工:员工信息更新成功")
        else:
            logger.error("角色--经理级以上员工:员工信息更新失败")
        
        logger.info("程序调度完成.")
    except Exception as e:
        logger.error(f"任务执行出错: {str(e)}")

def main():
    """主函数 - 支持立即执行或定时任务"""
    parser = argparse.ArgumentParser(description='数据同步程序')
    parser.add_argument('--run-now', action='store_true', help='立即执行一次任务')
    args = parser.parse_args()
    
    if args.run_now:
        logger.info("开始立即执行任务...")
        job()
        return
    
    logger.info("启动定时任务调度器...")
    scheduler = BlockingScheduler()
    
    # 添加任务，每天凌晨2点执行
    scheduler.add_job(
        job,
        trigger=CronTrigger(hour=2, minute=0),
        id='daily_sync_job',
        name='每日数据同步任务',
        misfire_grace_time=3600
    )
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("调度器已停止")

if __name__ == "__main__":
    main()