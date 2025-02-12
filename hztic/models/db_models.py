from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Organization(Base):
    __tablename__ = "organizations"
    org_id = Column(String, primary_key=True)
    org_name = Column(String)
    person_in_charge = Column(String)
    person_in_charge_text = Column(String)
    extsuoshugongsizhuti = Column(String)
    extsuoshugongsizhuti_text= Column(String)
    tree_path= Column(String)
    tree_path_text= Column(String)

class Corporation(Base):
    __tablename__ = "corporations"
    corp_id = Column(String, primary_key=True)
    corp_name = Column(String)
    extzuzhidaima = Column(String)
    extkaihuyinhang = Column(String)
    extyinhangzhanghao = Column(String)
    extdianhua = Column(String)
    extdengjidizhi = Column(String)


class Employee(Base):
    __tablename__ = "employees"
    user_id = Column(String, primary_key=True)
    id_number = Column(String)
    job_number = Column(String)
    mobile_phone = Column(String)
    employee_name = Column(String)
    oId_job_level_id = Column(String)
    oId_department_id = Column(String)
    oId_job_level_text = Column(String)
    oId_department_text = Column(String)
    employee_status = Column(String)
    email = Column(String)
    service_type = Column(String)
    employment_form = Column(String)
    
class EmployeeStatus(Base):
    __tablename__ = "employee_status"
    id = Column(Integer, primary_key=True, autoincrement=True)
    status_code = Column(Integer, nullable=False, unique=True)  # 状态代码
    status_name = Column(String(50), nullable=False)            # 状态名称
    
    PREDEFINED_EMPLOYEE_STATUS_DATA = [                         # 预定义的员工状态数据
    {"status_code": 1, "status_name": "待入职"},
    {"status_code": 2, "status_name": "试用"},
    {"status_code": 3, "status_name": "正式"},
    {"status_code": 4, "status_name": "调出"},
    {"status_code": 5, "status_name": "待调入"},
    {"status_code": 6, "status_name": "退休"},
    {"status_code": 8, "status_name": "离职"},
    {"status_code": 12, "status_name": "非正式"}
]

class JobLevel(Base):
    __tablename__ = "job_level"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)                              # 职位级别
    object_id = Column(String(50), nullable=False, unique=True)            # 职位级别ID
    

class EmploymentForm(Base):
    __tablename__ = "employment_form"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)                              # 用工形式
    object_id = Column(String(50), nullable=False, unique=True)            # 用工形式ID
    

class Whitelist(Base):
    __tablename__ = "whitelist"  # 表名
    id = Column(Integer, primary_key=True, index=True)  # 主键
    staff_id = Column(String, unique=True, index=True)  # 员工工号，唯一
    is_deleted = Column(Boolean, default=False)  # 软删除标记，默认为 False