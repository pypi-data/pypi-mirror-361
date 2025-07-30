from fastapi import APIRouter

from cloe_api.api.api_v1.endpoints import (
    crawler,
    dataflow,
    exec_sql,
    full_model,
    repository,
)

api_router = APIRouter()

api_router.include_router(dataflow.router, prefix="/modeler", tags=["modeler"])

api_router.include_router(
    full_model.router,
    prefix="/full_model",
    tags=["validation"],
)

api_router.include_router(
    repository.router,
    prefix="/repository",
    tags=["repository"],
)

api_router.include_router(
    exec_sql.router,
    prefix="/exec_sql",
    tags=["jobs"],
)

api_router.include_router(
    crawler.router,
    prefix="/crawler",
    tags=["crawler"],
)
