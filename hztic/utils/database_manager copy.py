from sqlalchemy import inspect, DDL
from sqlalchemy.schema import CreateTable, DropTable, AddColumn, DropColumn, AlterColumn

def sync_table_structure(self):
    """同步表结构：检查表是否存在、字段是否缺失、字段属性是否正确、字段是否多余"""
    inspector = inspect(self.engine)
    existing_tables = inspector.get_table_names()

    with self.engine.connect() as conn:  # 复用同一个连接
        for table_name, table_class in Base.metadata.tables.items():
            if table_name not in existing_tables:
                # 如果表不存在，则创建表
                print(f"表 {table_name} 不存在，正在创建...")
                conn.execute(CreateTable(table_class))
            else:
                # 如果表存在，检查并同步字段
                existing_columns = {col["name"]: col for col in inspector.get_columns(table_name)}
                for column in table_class.columns:
                    if column.name not in existing_columns:
                        # 如果字段缺失，则添加字段
                        print(f"表 {table_name} 缺少列 {column.name}，正在添加...")
                        try:
                            conn.execute(AddColumn(table_name, column))
                        except Exception as e:
                            print(f"添加列 {column.name} 失败: {e}")
                            continue  # 继续处理其他列
                    else:
                        # 如果字段存在，检查字段属性是否一致
                        existing_column = existing_columns[column.name]
                        if not self._compare_column_properties(column, existing_column):
                            print(f"表 {table_name} 的列 {column.name} 属性不一致，正在更新...")
                            try:
                                conn.execute(AlterColumn(table_name, column))
                            except Exception as e:
                                print(f"更新列 {column.name} 失败: {e}")
                                continue  # 继续处理其他列

                # 检查是否有多余的字段
                model_columns = {col.name for col in table_class.columns}
                for existing_column_name in existing_columns:
                    if existing_column_name not in model_columns:
                        print(f"表 {table_name} 有多余的列 {existing_column_name}，正在删除...")
                        try:
                            conn.execute(DropColumn(table_name, existing_column_name))
                        except Exception as e:
                            print(f"删除列 {existing_column_name} 失败: {e}")
                            continue  # 继续处理其他列

def _compare_column_properties(self, column, existing_column):
    """比较字段属性是否一致"""
    # 检查字段类型
    if str(column.type) != existing_column["type"]:
        return False
    # 检查字段是否允许为空
    if column.nullable != existing_column["nullable"]:
        return False
    # 检查字段默认值
    if column.default != existing_column["default"]:
        return False
    # 其他属性检查（如长度、唯一性等）
    return True