from enum import Enum

from cloe_metadata import base
from cloe_metadata_to_ddl import utils as ddl_utils
from fastapi import APIRouter

from cloe_api import utils

router = APIRouter()


class OutputSQLSystemType(str, Enum):
    t_sql = "t_sql"
    snowflake_sql = "snowflake_sql"


@router.post("/preview/{output_sql_system_type}")
def preview(
    output_sql_system_type: OutputSQLSystemType,
    databases: base.Databases,
) -> str:
    template_env = ddl_utils.load_package(output_sql_system_type.value)
    return ddl_utils.create_script_from_db_model(
        databases=databases, template_env=template_env
    )


@router.post("/ddl_files/{output_sql_system_type}")
def ddl_files(
    output_sql_system_type: OutputSQLSystemType,
    databases: base.Databases,
) -> list[dict[str, str | list]]:
    template_env = ddl_utils.load_package(output_sql_system_type.value)
    return utils.create_db_model_file_structure_from_db_model(
        databases=databases, template_env=template_env
    )
