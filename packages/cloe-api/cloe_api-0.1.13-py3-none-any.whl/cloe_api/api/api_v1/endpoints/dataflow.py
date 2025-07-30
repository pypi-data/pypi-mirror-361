import re
import uuid
from enum import Enum

import jinja2
from cloe_metadata import base
from cloe_metadata.utils import model_transformer
from cloe_sql_transformations import model as transform_model
from cloe_sql_transformations.model import sql_syntax as transform_sql_syntax
from cloe_sql_transformations.utils import engine_templates as utils_engine_templates
from cloe_sql_transformations.utils import render_sql_script
from cloe_sql_transformations.utils import transform as transform_utils
from fastapi import APIRouter, Body, HTTPException

router = APIRouter()


class OutputSQLSystemType(str, Enum):
    t_sql = "t_sql"
    snowflake_sql = "snowflake_sql"


@router.post("/preview/{output_sql_system_type}")
def preview(
    output_sql_system_type: OutputSQLSystemType,
    dataflows: base.Flows,
    tenants: base.Tenants,
    conversion_templates: base.ConversionTemplates,
    sql_templates: base.SQLTemplates,
    engine_templates: base.SQLTemplates,
    databases: base.Databases,
) -> str:
    is_tsql = output_sql_system_type is OutputSQLSystemType.t_sql
    is_snowflake = output_sql_system_type is OutputSQLSystemType.snowflake_sql
    default_engine_templates = utils_engine_templates.EngineTemplates(output_sql_system_type.value)
    default_engine_templates.merge_custom_templates(engine_templates)
    trans_dataflows, t_pp_errors = model_transformer.transform_power_pipes_to_shared(
        base_obj_collection=dataflows,
        databases=databases,
        tenants=tenants,
        conversion_templates=conversion_templates,
        sql_templates=sql_templates,
    )
    (
        trans_custom_dataflows,
        t_sp_errors,
    ) = model_transformer.transform_simple_pipes_to_shared(
        base_obj_collection=dataflows,
        databases=databases,
    )
    if len(t_pp_errors) > 0 or len(t_sp_errors) > 0:
        raise HTTPException(
            status_code=422,
            detail="Unprocessable Entity - Please run validation.",
        )
    sql_syntax = transform_sql_syntax.SQLSyntax(
        engine_templates=default_engine_templates,
        is_tsql=is_tsql,
        is_snowflake=is_snowflake,
    )
    trans_flows = transform_utils.transform_pipes(
        dataflows=trans_dataflows,
        custom_dataflows=trans_custom_dataflows,
        sql_syntax=sql_syntax,
        object_identifier_template=jinja2.Template(default_engine_templates.object_identifier),
    )
    trans_targettype_to_conversion = transform_utils.transform_common(
        conversion_templates=conversion_templates, sql_syntax=sql_syntax
    )
    return render_sql_script.render_sql_script(
        trans_flows,
        trans_targettype_to_conversion,
    )


@router.post("/preview/dq/{output_sql_system_type}")
def preview_dq(
    output_sql_system_type: OutputSQLSystemType,
    dataflows: base.Flows,
    tenants: base.Tenants,
    conversion_templates: base.ConversionTemplates,
    sql_templates: base.SQLTemplates,
    engine_templates: base.SQLTemplates,
    databases: base.Databases,
) -> str:
    is_tsql = output_sql_system_type is OutputSQLSystemType.t_sql
    is_snowflake = output_sql_system_type is OutputSQLSystemType.snowflake_sql
    default_engine_templates = utils_engine_templates.EngineTemplates(output_sql_system_type.value)
    default_engine_templates.merge_custom_templates(engine_templates)
    trans_dataflows, t_pp_errors = model_transformer.transform_power_pipes_to_shared(
        base_obj_collection=dataflows,
        databases=databases,
        tenants=tenants,
        conversion_templates=conversion_templates,
        sql_templates=sql_templates,
    )
    (
        trans_custom_dataflows,
        t_sp_errors,
    ) = model_transformer.transform_simple_pipes_to_shared(
        base_obj_collection=dataflows,
        databases=databases,
    )
    if len(t_pp_errors) > 0 or len(t_sp_errors) > 0:
        raise HTTPException(
            status_code=422,
            detail="Unprocessable Entity.",
        )
    sql_syntax = transform_sql_syntax.SQLSyntax(
        engine_templates=default_engine_templates,
        is_tsql=is_tsql,
        is_snowflake=is_snowflake,
    )
    trans_flows = transform_utils.transform_pipes(
        dataflows=trans_dataflows,
        custom_dataflows=trans_custom_dataflows,
        sql_syntax=sql_syntax,
        object_identifier_template=jinja2.Template(default_engine_templates.object_identifier),
    )
    trans_targettype_to_conversion = transform_utils.transform_common(
        conversion_templates=conversion_templates, sql_syntax=sql_syntax
    )
    dq_views: dict[str, str] = {}
    if is_tsql:
        output_sql_transaction_separator = ";\nGO"
    if is_snowflake:
        output_sql_transaction_separator = ";\n"
    for dataflow in trans_flows:
        if isinstance(dataflow, transform_model.DataflowGenerator):
            dataflow.gen_exec_sql_query(trans_targettype_to_conversion)
            dq_views |= dataflow.gen_dq_views(output_sql_transaction_separator)
    complete_file = ""
    for dq_key, out in dq_views.items():
        complete_file += f"\n\n\n\n--NEXT Table STARTING {dq_key}\n{out}"
    return complete_file


@router.post("/ddl_files/dq/{output_sql_system_type}")
def ddl_files(
    output_sql_system_type: OutputSQLSystemType,
    dataflows: base.Flows,
    tenants: base.Tenants,
    conversion_templates: base.ConversionTemplates,
    sql_templates: base.SQLTemplates,
    engine_templates: base.SQLTemplates,
    databases: base.Databases,
) -> list[dict[str, str | int]]:
    is_tsql = output_sql_system_type is OutputSQLSystemType.t_sql
    is_snowflake = output_sql_system_type is OutputSQLSystemType.snowflake_sql
    default_engine_templates = utils_engine_templates.EngineTemplates(output_sql_system_type.value)
    default_engine_templates.merge_custom_templates(engine_templates)
    trans_dataflows, t_pp_errors = model_transformer.transform_power_pipes_to_shared(
        base_obj_collection=dataflows,
        databases=databases,
        tenants=tenants,
        conversion_templates=conversion_templates,
        sql_templates=sql_templates,
    )
    (
        trans_custom_dataflows,
        t_sp_errors,
    ) = model_transformer.transform_simple_pipes_to_shared(
        base_obj_collection=dataflows,
        databases=databases,
    )
    if len(t_pp_errors) > 0 or len(t_sp_errors) > 0:
        raise HTTPException(
            status_code=422,
            detail="Unprocessable Entity.",
        )
    sql_syntax = transform_sql_syntax.SQLSyntax(
        engine_templates=default_engine_templates,
        is_tsql=is_tsql,
        is_snowflake=is_snowflake,
    )
    trans_flows = transform_utils.transform_pipes(
        dataflows=trans_dataflows,
        custom_dataflows=trans_custom_dataflows,
        sql_syntax=sql_syntax,
        object_identifier_template=jinja2.Template(default_engine_templates.object_identifier),
    )
    dq_views: list[dict[str, str | int]] = []
    trans_targettype_to_conversion = transform_utils.transform_common(
        conversion_templates=conversion_templates, sql_syntax=sql_syntax
    )
    for dataflow in trans_flows:
        if isinstance(dataflow, transform_model.DataflowGenerator):
            dataflow.gen_exec_sql_query(trans_targettype_to_conversion)
            dq_views += dataflow.gen_dq_views_json()
    return dq_views


@router.post("/auto_column_mapping/{output_sql_system_type}")
def auto_column_mapping(
    source_table_ids: list[uuid.UUID],
    conversion_templates: base.ConversionTemplates,
    databases: base.Databases,
    output_sql_system_type: OutputSQLSystemType,
    sink_table_id: uuid.UUID = Body(),
) -> list[dict]:
    sink_table: base.Table | None = databases.id_to_tables.get(sink_table_id, None)
    source_tables: list[base.Table | None] = [
        databases.id_to_tables.get(source_table_id, None) for source_table_id in source_table_ids
    ]
    if sink_table is None or not all(source_tables):
        raise HTTPException(
            status_code=400,
            detail=("Sink_table_id or source_table_ids were either empty or not found in databases."),
        )
    sink_columns = {column.name: column for column in sink_table.columns}
    source_table_columns: list[list[base.repository.database.column.Column]] = [
        source_table.columns for source_table in source_tables if source_table is not None
    ]
    source_column_names: list[list[str]] = []
    for columns in source_table_columns:
        source_column_names.append([column.name for column in columns])
    source_column_name_union: set[str] = set().union(*source_column_names)
    only_alpha = re.compile(r"[^A-Za-z0-9]+")
    source_column_names_alpha: dict[str, base.repository.database.column.Column] = {
        only_alpha.sub("", column.name): column
        for column in source_table_columns[0]
        if column.name in source_column_name_union
    }
    sink_column_names_alpha = {only_alpha.sub("", column_name): column for column_name, column in sink_columns.items()}
    column_mappings: list[base.modeler.dataflow.ColumnMapping] = []
    simplified_name_conversion: dict[str, base.ConversionTemplate] = {}
    for conversion in conversion_templates.conversion_templates:
        simplified_name = conversion.output_type.split("(")[0].split("_")[0]
        if simplified_name not in simplified_name_conversion:
            simplified_name_conversion[simplified_name] = conversion
    for column_name, column in source_column_names_alpha.items():
        if column_name in sink_column_names_alpha:
            datatype_conversion = None
            sink_datatype = sink_column_names_alpha[column_name].data_type
            if column.data_type != sink_datatype:
                if sink_datatype in simplified_name_conversion:
                    datatype_conversion = simplified_name_conversion[sink_datatype].output_type
            column_mappings.append(
                base.modeler.dataflow.ColumnMapping(
                    source_column_name=source_column_names_alpha[column_name].name,
                    sink_column_name=sink_column_names_alpha[column_name].name,
                    sink_table_id=sink_table_id,
                    convert_to_datatype=datatype_conversion,
                )
            )
    return [
        column_mapping.model_dump(
            exclude_none=True,
            by_alias=True,
        )
        for column_mapping in sorted(column_mappings, key=lambda p: p.source_column_name or "")
    ]
