from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, inspect, DDL
from hztic.models.db_models import Base, Organization, Employee, EmployeeStatus, JobLevel, EmploymentForm, Corporation
import os
from hztic.utils.logger import Logger

class DatabaseManager:
    """数据库管理器，用于管理数据库连接和数据操作。"""

    def __init__(self):
        self.logger = Logger(name=self.__class__.__name__).get_logger()
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.DATABASE_PATH = os.path.join(self.BASE_DIR, "data", "db", "app.db")
        self.DATABASE_URL = f"sqlite:///{self.DATABASE_PATH}"
        self.engine = create_engine(self.DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.logger.debug("DB connection init done. URL: %s", self.DATABASE_URL)
        self.sync_table_structure()

    def sync_table_structure(self):
        """同步表结构"""
        inspector = inspect(self.engine)
        existing_tables = inspector.get_table_names()

        with self.engine.connect() as conn:
            for table_name, table_class in Base.metadata.tables.items():
                if table_name not in existing_tables:
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
            existing_emp = session.query(Employee).filter(
                Employee.user_id == emp.user_id
            ).first()
            if existing_emp:
                self.logger.debug("Field user_id: %s exists, updating...", emp.user_id)
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
                self.logger.debug("Field user_id: %s not found, inserting...", emp.user_id)
                db_emp = Employee(**emp.__dict__)
                session.add(db_emp)
            session.commit()
            self.logger.debug("Save user_id: %s success.", emp.user_id)
        except Exception as e:
            session.rollback()
            self.logger.error("Save user_id: %s failed: %s", emp.user_id, e)
            raise e
        finally:
            session.close()
            
    def save_job_level(self, job_level):
        """保存职级信息到数据库（如果已存在则更新）"""
        session = self.SessionLocal()
        try:
            existing_job_level = session.query(JobLevel).filter(
                JobLevel.name == job_level.name
            ).first()
            if existing_job_level:
                existing_job_level.object_id = job_level.object_id
            else:
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
                existing_employment_form.object_id = employment_form.object_id
            else:
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
            existing_corp = session.query(Corporation).filter(
                Corporation.corp_id == corp.corp_id
            ).first()
            if existing_corp:
                existing_corp.corp_name = corp.corp_name
                existing_corp.extdengjidizhi = corp.extdengjidizhi
                existing_corp.extdianhua = corp.extdianhua
                existing_corp.extkaihuyinhang = corp.extkaihuyinhang
                existing_corp.extyinhangzhanghao = corp.extyinhangzhanghao
                existing_corp.extzuzhidaima = corp.extzuzhidaima
            else:
                db_corp = Corporation(**corp.__dict__)
                session.add(db_corp)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            
    def get_organization_staff_mapping(self, path_type="name"):
        """
        获取组织部门与员工的映射关系。

        :param path_type: 路径类型，可选值为 "name"（名称）、"code"（编码）、"id"(ID),默认为 "name"
        :return: 返回组织部门与员工的映射关系列表
        """
        session = self.SessionLocal()
        try:
            # 查询 organizations 表中的 person_in_charge 和 tree_path_text
            org_data = session.query(
                Organization.person_in_charge,
                Organization.tree_path_text
            ).all()

            result = []
            for person_in_charge, tree_path_text in org_data:
                if not person_in_charge or not tree_path_text:
                    continue

                # 根据 person_in_charge 匹配 employees 表中的 user_id，获取 job_number
                employee = session.query(Employee.job_number).filter(
                    Employee.user_id == person_in_charge
                ).first()

                if not employee:
                    continue

                # 解析 tree_path_text 为路径列表
                path_list = tree_path_text.split("/")

                # 根据 path_type 确定路径类型
                if path_type == "code":
                    # 假设 tree_path_text 是编码路径，直接使用
                    path_list = tree_path_text.split("/")
                elif path_type == "id":
                    # 假设 tree_path_text 是 ID 路径，直接使用
                    path_list = tree_path_text.split("/")
                else:
                    # 默认使用名称路径
                    path_list = tree_path_text.split("/")

                # 构建返回数据结构
                mapping = {
                    "pathType": path_type,
                    "path": path_list,
                    "staffs": [employee.job_number]
                }

                # 检查是否已存在相同路径的映射，避免重复
                existing_mapping = next((item for item in result if item["path"] == path_list), None)
                if existing_mapping:
                    existing_mapping["staffs"].append(employee.job_number)
                else:
                    result.append(mapping)

            return result

        except Exception as e:
            self.logger.error("获取组织部门与员工映射关系失败: %s", e)
            raise e
        finally:
            session.close()
        
        
    def get_manager_org_path(self):
        """
        获取经理级以上员工的工号及部门路径信息
        :return: 返回包含经理级以上员工的部门路径信息列表，格式为：
            [
                {
                    "pathType": "name",
                    "path": ["总公司", "部门A", "子部门B"],
                    "staffs": ["1001", "1002"]
                },
                ...
            ]
        """
        session = self.SessionLocal()
        try:
            # 查询经理级以上员工
            managers = session.query(
                Employee.job_number,
                Employee.oId_department_id
            ).filter(
                Employee.employee_status.in_(["2", "3"])
                
            ).filter(
                Employee.oId_job_level_text.in_(["经理级", "总经理级"])
            ).all()
            result = []
            for job_number, department_id in managers:
                if not department_id:
                    continue
                # 查询对应的部门路径
                org = session.query(Organization.tree_path_text).filter(
                    Organization.org_id == department_id
                ).first()
                if not org or not org.tree_path_text:
                    continue
                # 解析路径
                path_list = org.tree_path_text.split("/")
                # 查找是否已有相同路径的记录
                existing = next((item for item in result if item["path"] == path_list), None)
                if existing:
                    existing["staffs"].append(job_number)
                else:
                    result.append({
                        "pathType": "name",
                        "path": path_list,
                        "staffs": [job_number]
                    })
            return result
        except Exception as e:
            self.logger.error("获取经理级员工部门路径失败: %s", e)
            raise e
        finally:
            session.close()