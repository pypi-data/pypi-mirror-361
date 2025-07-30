import logging
from typing import Any

from cloe_metadata import base
from cloe_metadata.shared.jobs import exec_sql

from cloe_metadata_to_ddl.utils import templating_engine

logger = logging.getLogger(__name__)


def get_procedure_call(
    job: exec_sql.ExecSQL,
) -> Any:
    snowflake_sql_template_env = templating_engine.load_package("snowflake_sql")
    t_sql_template_env = templating_engine.load_package("t_sql")
    sink_connection = job.sink_connection
    if sink_connection.system_type in (
        sink_connection.azure_synapse_key,
        sink_connection.azure_server_nativ_key,
        sink_connection.sql_server_nativ_key,
    ):
        template = t_sql_template_env.get_template("procedure_call.sql.j2")
        return template.render(
            procedure_name=job.get_procedure_name(),
            parameters={},
        )
    if sink_connection.system_type in (sink_connection.snowflake_nativ_key):
        template = snowflake_sql_template_env.get_template("procedure_call.sql.j2")
        return template.render(
            procedure_name=job.get_procedure_name(),
            parameters={},
        )
    logger.error(
        "No call stored procedure templates for system_type %s",
        sink_connection.system_type,
    )
    raise NotImplementedError


def get_procedure_call_with_parameters(
    job: exec_sql.ExecSQL,
    proc_parameters: dict[str, str],
    escape_quote_params: bool = True,
) -> Any:
    snowflake_sql_template_env = templating_engine.load_package("snowflake_sql")
    t_sql_template_env = templating_engine.load_package("t_sql")
    sink_connection = job.sink_connection
    quote_character = "''"
    if not escape_quote_params:
        quote_character = "'"
    if sink_connection.system_type in (
        sink_connection.azure_synapse_key,
        sink_connection.azure_server_nativ_key,
        sink_connection.sql_server_nativ_key,
    ):
        template = t_sql_template_env.get_template("procedure_call.sql.j2")
        return template.render(
            procedure_name=job.get_procedure_name(),
            parameters=proc_parameters,
            escape_character=quote_character,
        )
    if sink_connection.system_type in (sink_connection.snowflake_nativ_key):
        template = snowflake_sql_template_env.get_template("procedure_call.sql.j2")
        return template.render(
            procedure_name=job.get_procedure_name(),
            parameters=proc_parameters,
            escape_character=quote_character,
        )
    logger.error(
        "No call stored procedure with parameters templates for system_type %s",
        sink_connection.system_type,
    )
    raise NotImplementedError


def get_procedure_create(
    job: exec_sql.ExecSQL,
    is_transaction: bool = False,
    use_monitoring: bool = False,
) -> Any:
    snowflake_sql_template_env = templating_engine.load_package("snowflake_sql")
    t_sql_template_env = templating_engine.load_package("t_sql")
    sink_connection = job.sink_connection
    if sink_connection.system_type in (
        sink_connection.azure_synapse_key,
        sink_connection.azure_server_nativ_key,
        sink_connection.sql_server_nativ_key,
    ):
        template = t_sql_template_env.get_template("procedure_create.sql.j2")
        queries = [query.query for query in sorted(job.base_obj.queries, key=lambda x: x.exec_order)]
        return template.render(
            procedure_name=job.get_procedure_name(),
            queries=queries,
        )
    if sink_connection.system_type in (sink_connection.snowflake_nativ_key):
        queries = [query.query.replace("\n", " ") for query in sorted(job.base_obj.queries, key=lambda x: x.exec_order)]
        template = snowflake_sql_template_env.get_template("procedure_create.sql.j2")
        return template.render(
            procedure_name=job.get_procedure_name(),
            queries=queries,
            is_transaction=is_transaction,
            parameters={},
            use_monitoring=use_monitoring,
        )
    logger.error(
        "No create stored procedure templates for system_type %s",
        sink_connection.system_type,
    )
    raise NotImplementedError


def get_query_postfix(base_obj: base.Connection) -> str:
    if base_obj.system_type in (
        base_obj.azure_synapse_key,
        base_obj.azure_server_nativ_key,
        base_obj.sql_server_nativ_key,
    ):
        return "\n\nGO\n\n"
    if base_obj.system_type in (base_obj.snowflake_nativ_key):
        return "\n\n"
    logger.error("No query postfix templates for system_type %s", base_obj.system_type)
    raise NotImplementedError
