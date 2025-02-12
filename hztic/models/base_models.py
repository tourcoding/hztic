from dataclasses import dataclass
from typing import Optional


@dataclass
class Organization:
    org_id: str                                         # 组织ID
    org_name: str                                       # 组织名称
    extsuoshugongsizhuti: Optional[str] = None          # 所属公司主体ID
    person_in_charge: Optional[str] = None              # 部门负责人USER_ID
    person_in_charge_text: Optional[str] = None         # 部门负责人信息
    tree_path: Optional[str] = None                     # 组织树路径
    tree_path_text: Optional[str] = None                # 组织树路径文本
    extsuoshugongsizhuti_text: Optional[str] = None     # 所属公司主体文本

@dataclass
class Corporation:
    corp_id: str                               # 公司ID
    corp_name: str                             # 公司名称
    extzuzhidaima: Optional[str] = None        # 组织机构代码
    extkaihuyinhang: Optional[str] = None      # 开户银行
    extyinhangzhanghao: Optional[str] = None   # 银行账号
    extdianhua: Optional[str] = None           # 电话
    extdengjidizhi: Optional[str] = None       # 登记地址

@dataclass
class Employee:
    user_id: str                                 # 用户ID
    id_number: Optional[str] = None              # 身份证号
    job_number: Optional[str] = None             # 工号
    mobile_phone: Optional[str] = None           # 手机号
    employee_name: Optional[str] = None          # 员工姓名
    oId_job_level_id: Optional[str] = None       # 职级ID
    oId_department_id: Optional[str] = None      # 部门ID
    oId_job_level_text: Optional[str] = None     # 职级名称
    oId_department_text: Optional[str] = None    # 部门名称
    employee_status: Optional[str] = None        # 员工状态
    email: Optional[str] = None                  # 邮箱
    service_type: Optional[str] = None           # 服务类型
    employment_form: Optional[str] = None        # 用工形式
    
@dataclass
class JobLevel:
    name: str                                    # 职级名称
    object_id: str                               # 职级ID    
    
@dataclass
class EmploymentForm:
    name: str                                    # 用工形式名称
    object_id: str                               # 用工形式ID