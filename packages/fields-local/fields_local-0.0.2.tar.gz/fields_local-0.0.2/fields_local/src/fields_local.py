from logger_local.LoggerLocal import Logger
from database_mysql_local.generic_crud_mysql import GenericCrudMysql
from logger_local.LoggerComponentEnum import LoggerComponentEnum

from .constants_src_fields_local import ConstantsSrcFieldsLocal


FIELD_SCHEMA_NAME = "field"
FIELD_TABLE_NAME = "field_table"
FIELD_VIEW_NAME = "field_view"
FIELD_GENERAL_VIEW_NAME = "field_general_view"

FIELD_LOCAL_PYTHON_PACKAGE_COMPONENT_ID = 229
FIELD_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME = "field_main_local_python"
DEVELOPER_EMAIL = "zvi.n@circ.zone"

object_init = {
    "component_id": FIELD_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,
    "component_name": FIELD_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME,
    "component_category": LoggerComponentEnum.ComponentCategory.Code.value,
    "developer_email": DEVELOPER_EMAIL,
}

class FieldsLocal(GenericCrudMysql):
    
    def __init__(self, is_test_data: bool = False):
        super().__init__(
            default_schema_name=FIELD_SCHEMA_NAME,
            default_table_name=FIELD_TABLE_NAME,
            default_view_table_name=FIELD_VIEW_NAME, 
            is_test_data=is_test_data
        )

    def get_variable_id_name_dict(self, where: str = None, params:tuple = None) -> dict[int,str]:
        rows = self.select_multi_dict_by_where(
            select_clause_value="variable_id, name",
            view_table_name="variable_view",
            where=where,
            params=params,
            )
        data = {}
        for row in rows:
            data[row['variable_id']] = row['name']
        return data
    
    def get_variable_id_by_name(self, name: str):
        variable_id = self.select_one_value_by_where(
            select_clause_value="variable_id",
            where="name=%s",
            params=(name,)
        )
        return variable_id
    
    def get_field_id_by_alias_name(self, name: str):
        field_id = self.select_one_value_by_where(
            view_table_name="field_alias_view",
            select_clause_value="field_id",
            where="field_name=%s",
            params=(name,)
        )
        return field_id

    def get_database_field_name_by_field_id(self, field_id: int):
        field_id = self.select_one_value_by_where(
            select_clause_value="database_field_name",
            where="field_id=%s",
            params=(field_id,)
        )
        return field_id
    
    def get_table_id_by_field_id(self, field_id: int):
        field_id = self.select_one_value_by_where(
            select_clause_value="table_id",
            where="field_id=%s",
            params=(field_id,)
        )
        return field_id
    
    def get_table_schema_by_table_id(self, table_id: int):
        pass

    def get_table_name_by_table_id(self, table_id: int):
        pass

    def get_table_view_name_by_table_id(self, table_id: int):
        pass

    def get_table_schema_by_field_id(self, table_id: int):
        pass

    def get_table_name_by_field_id(self, table_id: int):
        pass

    def get_table_view_name_by_field_id(self, table_id: int):
        pass