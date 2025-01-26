from datetime import datetime
from typing import Dict
from hztic.services.beisen import BeisenOpenAPI
from hztic.utils.database_manager import DatabaseManager
from hztic.utils.logger import Logger

logger = Logger().get_logger()

def fetch_and_store_data(config: Dict, start_time: datetime, end_time: datetime):
    """Fetching data from Beisen API and storing to database."""
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
    
