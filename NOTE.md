**1。激活账户**

按部门

按角色（部门负责人）

白名单（其他操作的激活或禁用操作不会影响到白名单）


接口：授权员工

**2。同步角色  部门负责人**

北森API

（1）根据时间窗滚动查询变动的组织单元信息： /TenantBaseExternal/api/v5/Organization/GetByTimeWindow

    获取部门全称"POIdOrgAdminNameTreePathText"及部门负责人"PersonInCharge"

（2）获取员工信息(根据PersonInCharge 获取员工工号)   /UserFrameworkApiV3/api/v1/staffs/Get

合思费控：

（3）更新更新角色下员工信息   /api/openapi/v1.1/roledefs/$ID01EjGAFgd2N1:leader/staffs

**3。同步角色  经理级别及以上**

北森API：

（1）根据时间窗滚动查询变动的员工与单条任职信息   /TenantBaseExternal/api/v5/Employee/GetByTimeWindow

    查询员工工号及职级（经理级别及以上）

合思费控：

（2）删除角色下员工信息          **/api/openapi/v1.1/roledefs/$roledefId/staffs**

（2）更新更新角色下员工信息     /api/openapi/v1.1/roledefs/$ID01EQlDrnHJ8z/staffs
