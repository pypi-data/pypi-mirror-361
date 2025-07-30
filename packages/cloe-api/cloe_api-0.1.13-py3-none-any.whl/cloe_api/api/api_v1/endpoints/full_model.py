from typing import Any, cast

import pydantic
from cloe_metadata import base
from cloe_metadata.utils import model_transformer
from cloe_sql_transformations.utils import engine_templates as utils_engine_templates
from fastapi import APIRouter

router = APIRouter()


def extract_ids_for_errors(root_object, errors) -> list[dict[str, Any]]:
    """
    Extracts IDs of models that caused validation errors.
    """
    for error in errors:
        loc = error.get("loc", [])
        current_object = root_object
        for part in loc[
            :-1
        ]:  # Exclude the last part, which is the attribute that failed validation
            if isinstance(part, int):
                # Assuming the current object is a list or a list-like object
                next_object = current_object[part]
            else:
                # Assuming the current object is an object with attributes or a dictionary
                next_object = current_object.get(part)
            if next_object is not None:
                current_object = next_object

        # Assuming the final object has an 'id' attribute
        model_id = current_object.get("id", None)
        error["modelID"] = model_id
    error_payload = []
    for sub_errors in errors:
        error_payload.append(
            {k: sub_errors[k] for k in ["type", "msg", "modelID"] if k in sub_errors}
        )

    return error_payload


@router.post("/validation/basic")
def validate(
    batches: dict = {},
    connections: dict = {},
    jobs: dict = {},
    databases: dict = {},
    data_source_infos: dict = {},
    dataset_types: dict = {},
    sourcesystems: dict = {},
    tenants: dict = {},
    conversion_templates: dict = {},
    sql_templates: dict = {},
    engine_templates: dict = {},
    datatype_templates: dict = {},
    dataflows: dict = {},
) -> dict:
    all_errors = {}
    models: list[tuple[object, dict]] = [
        (base.Batches, batches),
        (base.Connections, connections),
        (base.Jobs, jobs),
        (base.Databases, databases),
        (base.DataSourceInfos, data_source_infos),
        (base.DatasetTypes, dataset_types),
        (base.Sourcesystems, sourcesystems),
        (base.Tenants, tenants),
        (base.ConversionTemplates, conversion_templates),
        (base.SQLTemplates, sql_templates),
        (base.SQLTemplates, engine_templates),
        (base.DatatypeTemplates, datatype_templates),
        (base.Flows, dataflows),
    ]

    for model_type in models:
        if len(model_type[1]) < 1:
            continue
        base_model: pydantic.BaseModel = cast(pydantic.BaseModel, model_type[0])
        try:
            base_model.model_validate(model_type[1])
            content = {"errorCount": 0, "errors": {}}
        except pydantic.ValidationError as e:
            error_obj = e.errors()
            model_errors = extract_ids_for_errors(model_type[1], error_obj)
            all_errors[base_model.__name__] = model_errors  # type: ignore
    content = {
        "errorCount": sum([len(class_error) for class_error in all_errors.values()]),
        "errors": all_errors,
    }
    return content


@router.post("/validation/advanced")
def validate_advanced_dataflows(
    dataflows: base.Flows,
    tenants: base.Tenants,
    conversion_templates: base.ConversionTemplates,
    sql_templates: base.SQLTemplates,
    engine_templates: base.SQLTemplates,
    databases: base.Databases,
    jobs: base.Jobs,
    connections: base.Connections,
    data_source_infos: base.DataSourceInfos,
    dataset_types: base.DatasetTypes,
    sourcesystems: base.Sourcesystems,
) -> dict:
    default_engine_templates = utils_engine_templates.EngineTemplates("snowflake_sql")
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
    exec_sqls, e_errors = model_transformer.transform_exec_sql_to_shared(
        base_obj_collection=jobs,
        connections=connections,
    )
    (
        shared_data_source_infos,
        s_dsi_errors,
    ) = model_transformer.transform_data_source_info_to_shared(
        data_source_infos,
        sourcesystems=sourcesystems,
        tenants=tenants,
    )
    db2fss, s_db2fs_errors = model_transformer.transform_db2fs_to_shared(
        jobs,
        data_source_infos=shared_data_source_infos,
        dataset_types=dataset_types,
        databases=databases,
        connections=connections,
    )
    fs2dbs, s_fs2db_errors = model_transformer.transform_fs2db_to_shared(
        jobs,
        dataset_types=dataset_types,
        databases=databases,
        connections=connections,
        exec_sqls=exec_sqls,
    )
    all_errors = {
        "Dataflow": t_pp_errors,
        "CustomDataflow": t_sp_errors,
        "ExecSQL": e_errors,
        "DataSourceInfo": s_dsi_errors,
        "DB2FS": s_db2fs_errors,
        "FS2DB": s_fs2db_errors,
    }
    error_payload = {}
    for obj_name, id_to_errors in all_errors.items():
        transformed_errors = []
        for obj_id, errors in id_to_errors.items():
            for error in errors:
                for error_details in error.errors():
                    custom_error = {}
                    custom_error["type"] = error_details["type"]
                    custom_error["msg"] = error_details["msg"]
                    custom_error["modelID"] = str(obj_id)
                    transformed_errors.append(custom_error)
        error_payload[obj_name] = transformed_errors
    content = {
        "errorCount": sum([len(class_error) for class_error in all_errors.values()]),
        "errors": error_payload,
    }
    return content
