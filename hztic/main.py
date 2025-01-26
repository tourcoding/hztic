from datetime import datetime, timedelta
from .config import BeisenAPIConfig
from hztic.handler.data_service import fetch_and_store_data
from hztic.utils.database_manager import DatabaseManager
from hztic.utils.logger import Logger

logger = Logger().get_logger()

def main():
    db_manager = DatabaseManager()
    db_manager.initialize_employee_status()
    
    # 配置时间范围
    # start_time = datetime(2023, 10, 23)
    # end_time = datetime(2025, 1, 25)
    
    start_time = datetime(2025, 1, 23)
    end_time = datetime(2025, 1, 26)

    # 获取北森数据并存储
    fetch_and_store_data(BeisenAPIConfig, start_time, end_time)
    logger.info("Main scheduling done.")
    
if __name__ == "__main__":
    main()