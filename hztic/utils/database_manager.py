from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, inspect, DDL
from hztic.models.db_models import Base, Organization, Employee, EmployeeStatus, JobLevel, EmploymentForm, Corporation
import os
from hztic.utils.logger import Logger

class DatabaseManager:
    """
    Database Manager Class
    
    Responsible for table schema synchronization, data initialization, and data persistence.
    """

    def __init__(self):
        # 数据库连接
        self.logger = Logger(name=self.__class__.__name__).get_logger()
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.DATABASE_PATH = os.path.join(self.BASE_DIR, "data", "db", "app.db")
        self.DATABASE_URL = f"sqlite:///{self.DATABASE_PATH}"
        self.engine = create_engine(self.DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.logger.debug("DB connection init done. URL: %s", self.DATABASE_URL)
        self.sync_table_structure()  # 初始化时自动同步表结构

    def sync_table_structure(self):
        """同步表结构：根据模型定义自动修改数据库表"""
        inspector = inspect(self.engine)
        existing_tables = inspector.get_table_names()

        with self.engine.connect() as conn:  # 复用同一个连接
            for table_name, table_class in Base.metadata.tables.items():
                if table_name not in existing_tables:
                    # 如果表不存在，则创建表
                    self.logger.info("Table %s not found, creating...", table_name)
                    table_class.create(conn)
                    self.logger.info("Table %s created successfully.", table_name)
                else:
                    # 如果表存在，检查并添加缺失的列
                    existing_columns = [col["name"] for col in inspector.get_columns(table_name)]
                    for column in table_class.columns:
                        if column.name not in existing_columns:
                            self.logger.info("Table %s is missing column %s, adding...", table_name, column.name)
                            try:
                                # 使用 SQLAlchemy 的 DDL 或 AddColumn 更安全
                                add_column_ddl = DDL(
                                    f"ALTER TABLE {table_name} ADD COLUMN {column.name} {column.type}"
                                )
                                conn.execute(add_column_ddl)
                                self.logger.info("Column %s added to table %s.", table_name, column.name)
                            except Exception as e:
                                self.logger.error("Failed to add column %s to table %s: %s", table_name, column.name, e)
                                continue  # 继续处理其他列

    def initialize_employee_status(self):
        """初始化 EmployeeStatus 表数据"""
        session = self.SessionLocal()
        try:
            # 检查表中是否已有数据
            existing_data = session.query(EmployeeStatus).count()
            if existing_data > 0:
                self.logger.debug("EmployeeStatus 表已初始化，跳过数据写入。")
                return

            # 插入预定义数据
            for status_data in EmployeeStatus.PREDEFINED_EMPLOYEE_STATUS_DATA:
                status = EmployeeStatus(**status_data)
                session.add(status)
            session.commit()
            self.logger.debug("EmployeeStatus表数据初始化完成。")
        except Exception as e:
            session.rollback()
            self.logger.error("初始化 EmployeeStatus 表数据失败, 错误信息: %s", e)
        finally:
            session.close()

    def save_organization(self, org):
        """保存组织数据到数据库（如果已存在则更新）"""
        session = self.SessionLocal()
        try:
            # 查询是否已存在
            existing_org = session.query(Organization).filter(
                Organization.org_id == org.org_id
            ).first()
            if existing_org:
                # 更新数据
                self.logger.debug("Field %s exists, updating...", org.org_id)
                existing_org.extsuoshugongsizhuti = org.extsuoshugongsizhuti
                existing_org.person_in_charge = org.person_in_charge
                existing_org.org_name = org.org_name
                existing_org.person_in_charge_text = org.person_in_charge_text
                existing_org.tree_path = org.tree_path
                existing_org.tree_path_text = org.tree_path_text
                existing_org.extsuoshugongsizhuti_text = org.extsuoshugongsizhuti_text
            else:
                # 插入新数据
                self.logger.debug("组织 %s 不存在，正在插入新数据...", org.org_id)
                db_org = Organization(**org.__dict__)
                session.add(db_org)
            session.commit()
            self.logger.debug("data %s save success。", org.org_id)
        except Exception as e:
            session.rollback()
            self.logger.error("保存组织 %s 数据失败: %s", org.org_id, e)
            raise e
        finally:
            session.close()

    def save_employee(self, emp):
        """保存员工数据到数据库（如果已存在则更新）"""
        session = self.SessionLocal()
        try:
            # 查询是否已存在
            existing_emp = session.query(Employee).filter(
                Employee.user_id == emp.user_id
            ).first()
            if existing_emp:
                # 更新数据
                self.logger.debug("Field %s exists, updating...", emp.user_id)
                existing_emp.id_number = emp.id_number
                existing_emp.job_number = emp.job_number
                existing_emp.mobile_phone = emp.mobile_phone
                existing_emp.employee_name = emp.employee_name
                existing_emp.oId_job_level_id = emp.oId_job_level_id
                existing_emp.oId_department_id = emp.oId_department_id
                existing_emp.oId_job_level_text = emp.oId_job_level_text
                existing_emp.oId_department_text = emp.oId_department_text
                existing_emp.employee_status = emp.employee_status
                existing_emp.email = emp.email
                existing_emp.service_type = emp.service_type
                existing_emp.employment_form = emp.employment_form
            else:
                # 插入新数据
                self.logger.debug("Field %s not found, inserting...", emp.user_id)
                db_emp = Employee(**emp.__dict__)
                session.add(db_emp)
            session.commit()
            self.logger.debug("Save %s success.", emp.user_id)
        except Exception as e:
            session.rollback()
            self.logger.error("Save %s failed: %s", emp.user_id, e)
            raise e
        finally:
            session.close()
            
    def save_job_level(self, job_level):
        """保存职级信息到数据库（如果已存在则更新）"""
        session = self.SessionLocal()
        try:
            # 查询是否已存在
            existing_job_level = session.query(JobLevel).filter(
                JobLevel.name == job_level.name
            ).first()
            if existing_job_level:
                # 更新数据
                existing_job_level.object_id = job_level.object_id
            else:
                # 插入新数据
                db_job_level = JobLevel(**job_level.__dict__)
                session.add(db_job_level)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            
            
    def save_employment_form(self, employment_form):
        """保存任职类型到数据库（如果已存在则更新）"""
        session = self.SessionLocal()
        try:
            # 查询是否已存在
            existing_employment_form = session.query(EmploymentForm).filter(
                EmploymentForm.name == employment_form.name
            ).first()
            if existing_employment_form:
                # 更新数据
                existing_employment_form.object_id = employment_form.object_id
            else:
                # 插入新数据
                db_employment_form = EmploymentForm(**employment_form.__dict__)
                session.add(db_employment_form)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            
    
    def save_corporation(self, corp):
        """保存员工数据到数据库（如果已存在则更新）"""
        session = self.SessionLocal()
        try:
            # 查询是否已存在
            existing_corp = session.query(Corporation).filter(
                Corporation.corp_id == corp.corp_id
            ).first()
            if existing_corp:
                # 更新数据
                existing_corp.corp_name = corp.corp_name
                existing_corp.extdengjidizhi = corp.extdengjidizhi
                existing_corp.extdianhua = corp.extdianhua
                existing_corp.extkaihuyinhang = corp.extkaihuyinhang
                existing_corp.extyinhangzhanghao = corp.extyinhangzhanghao
                existing_corp.extzuzhidaima = corp.extzuzhidaima
            else:
                # 插入新数据
                db_corp = Corporation(**corp.__dict__)
                session.add(db_corp)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()