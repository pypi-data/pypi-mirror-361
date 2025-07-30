import logging

from cloe_metadata import base
from cloe_snowflake_crawler import crawler as cloe_crawler
from cloe_snowflake_crawler import utils as crawl_utils
from cloe_util_snowflake_connector import connection_parameters, snowflake_interface
from fastapi import APIRouter
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class CrawlParameters(BaseModel):
    ignore_columns: bool = False
    ignore_tables: bool = False
    delete_old_databases: bool = False
    database_filter: str | None = None
    database_name_replace: str | None = None


@router.post("/crawl/snowflake")
def crawl(
    databases: base.Databases,
    connection_parameters: connection_parameters.ConnectionParameters,
    crawl_parameters: CrawlParameters,
) -> base.Databases:
    snowflake_conn = snowflake_interface.SnowflakeInterface(connection_parameters)
    crawler = cloe_crawler.SnowflakeCrawler(
        snf_interface=snowflake_conn,
        ignore_tables=crawl_parameters.ignore_tables,
        ignore_columns=crawl_parameters.ignore_columns,
        database_filter=crawl_parameters.database_filter,
        database_name_replace=crawl_parameters.database_name_replace,
    )
    crawler.crawl()
    crawled_databases = crawler.databases
    merged_databases = crawl_utils.merge_repository_content(crawled_databases, databases)
    if crawl_parameters.delete_old_databases is False:
        crawl_utils.restore_old_databases(databases=merged_databases, databases_old=databases)
    return merged_databases
