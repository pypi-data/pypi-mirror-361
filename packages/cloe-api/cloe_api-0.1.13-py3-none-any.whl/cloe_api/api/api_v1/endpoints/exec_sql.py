import uuid
from enum import Enum

import jinja2
from cloe_metadata import base
from cloe_metadata.base.jobs import exec_sql
from cloe_metadata.utils import model_transformer
from cloe_metadata_to_ddl import utils as ddl_utils
from cloe_sql_transformations import model
from cloe_sql_transformations.model import sql_syntax as transform_sql_syntax
from cloe_sql_transformations.utils import engine_templates as utils_engine_templates
from cloe_sql_transformations.utils import transform as transform_utils
from cloe_sql_transformations.utils.render_json_jobs import json_job_merger
from fastapi import APIRouter, HTTPException

router = APIRouter()


class OutputSQLSystemType(str, Enum):
    t_sql = "t_sql"
    snowflake_sql = "snowflake_sql"


@router.post("/transform/{output_sql_system_type}")
def transform(
    output_sql_system_type: OutputSQLSystemType,
    dataflows: base.Flows,
    tenants: base.Tenants,
    conversion_templates: base.ConversionTemplates,
    sql_templates: base.SQLTemplates,
    engine_templates: base.SQLTemplates,
    jobs: base.Jobs,
    databases: base.Databases,
) -> base.Jobs:
    is_tsql = output_sql_system_type is OutputSQLSystemType.t_sql
    is_snowflake = output_sql_system_type is OutputSQLSystemType.snowflake_sql
    default_engine_templates = utils_engine_templates.EngineTemplates(
        output_sql_system_type.value
    )
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
        object_identifier_template=jinja2.Template(
            default_engine_templates.object_identifier
        ),
    )
    trans_targettype_to_conversion = transform_utils.transform_common(
        conversion_templates=conversion_templates, sql_syntax=sql_syntax
    )
    generated_jobs = {}
    for dataflow in trans_flows:
        output_key = dataflow.job_id or uuid.uuid4()
        if isinstance(dataflow, model.DataflowGenerator):
            query = dataflow.gen_exec_sql_query(trans_targettype_to_conversion)
        elif isinstance(dataflow, model.CustomDataflowGenerator):
            query = dataflow.gen_job()
        else:
            raise HTTPException(
                status_code=400,
                detail="Unknown job type.",
            )
        exec_job = exec_sql.ExecSQL(
            id=output_key,
            name=dataflow.name,
            queries=query,
            connection_id=uuid.UUID(int=0),
        )
        generated_jobs[output_key] = exec_job
    return json_job_merger(generated_jobs, jobs)


@router.post("/preview")
def preview(
    jobs: base.Jobs,
    connections: base.Connections,
    transaction_based: bool = False,
    use_monitoring: bool = True,
) -> str:
    content = ""
    exec_sqls, e_errors = model_transformer.transform_exec_sql_to_shared(
        base_obj_collection=jobs,
        connections=connections,
    )
    if len(e_errors) > 0:
        raise HTTPException(
            status_code=422,
            detail="Unprocessable Entity.",
        )
    for job in exec_sqls.values():
        content += ddl_utils.get_procedure_create(
            job=job, is_transaction=transaction_based, use_monitoring=use_monitoring
        )
    return content


@router.post("/ddl_files")
def ddl_files(
    jobs: base.Jobs,
    connections: base.Connections,
    transaction_based: bool = False,
    use_monitoring: bool = True,
) -> list[dict[str, str]]:
    exec_sqls, e_errors = model_transformer.transform_exec_sql_to_shared(
        base_obj_collection=jobs,
        connections=connections,
    )
    if len(e_errors) > 0:
        raise HTTPException(
            status_code=422,
            detail="Unprocessable Entity.",
        )
    ddl_files = []
    for job in exec_sqls.values():
        create_query = ddl_utils.get_procedure_create(
            job=job, is_transaction=transaction_based, use_monitoring=use_monitoring
        )
        ddl_files.append({"id": str(job.base_obj.id), "content": create_query})
    return ddl_files
