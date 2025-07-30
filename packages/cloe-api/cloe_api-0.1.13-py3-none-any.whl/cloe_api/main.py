from fastapi import FastAPI

from cloe_api.api.api_v1.api import api_router

app = FastAPI()


@app.get("/health")
def read_root():
    return {"status": "healthy"}


app.include_router(api_router, prefix="/api/v1")
