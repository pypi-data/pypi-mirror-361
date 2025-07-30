import logging
import uuid

import jinja2
from cloe_metadata import base
from cloe_metadata_to_ddl.utils import create_ddl_from_db_model

logger = logging.getLogger(__name__)


def create_sql_file_structure_object(
    object_id: uuid.UUID | str, content: str
) -> dict[str, str]:
    return {
        "id": str(object_id),
        "content": content,
    }


def create_db_model_file_structure_from_db_model(
    databases: base.Databases,
    template_env: jinja2.Environment,
) -> list[dict[str, str | list]]:
    file_structure: list[dict[str, str | list]] = []
    for database in databases.databases:
        database_schemas = []
        database_ddl = create_ddl_from_db_model.generate_database_create_ddl(
            base_obj=database, template_env=template_env
        )
        for schema in database.schemas:
            schema_tables = []
            schema_ddl = create_ddl_from_db_model.generate_schema_create_ddl(
                base_obj=schema, template_env=template_env
            )
            for table in schema.tables:
                table_ddl = create_ddl_from_db_model.generate_table_create_ddl(
                    schema_base_obj=schema,
                    table_base_obj=table,
                    template_env=template_env,
                )
                schema_tables.append({"id": str(table.id), "content": table_ddl})
            database_schemas.append(
                {
                    "id": str(schema.id),
                    "content": schema_ddl,
                    "tables": schema_tables,
                }
            )
        file_structure.append(
            {
                "id": str(database.id),
                "content": database_ddl,
                "schemas": database_schemas,
            }
        )
    return file_structure
