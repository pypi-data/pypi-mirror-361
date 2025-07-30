import logging
import pathlib
from typing import Any

import cloe_metadata.utils.writer as writer
import jinja2
from cloe_metadata import base

logger = logging.getLogger(__name__)


def generate_database_create_ddl(base_obj: base.Database, template_env: jinja2.Environment) -> Any:
    ddl_template = template_env.get_template("create_database.sql.j2")
    return ddl_template.render(database=base_obj)


def generate_schema_create_ddl(base_obj: base.Schema, template_env: jinja2.Environment) -> Any:
    ddl_template = template_env.get_template("create_schema.sql.j2")
    return ddl_template.render(schema=base_obj)


def generate_table_create_ddl(
    schema_base_obj: base.Schema,
    table_base_obj: base.Table,
    template_env: jinja2.Environment,
) -> Any:
    ddl_template = template_env.get_template("create_table.sql.j2")
    return ddl_template.render(schema=schema_base_obj, table=table_base_obj)


def create_model_on_disk_from_db_model(
    output_path: pathlib.Path,
    databases: base.Databases,
    template_env: jinja2.Environment,
) -> None:
    """
    Create DDL from database model. Write result to disk.
    """
    for database in databases.databases:
        database_path = output_path / database.name
        database_ddl = generate_database_create_ddl(base_obj=database, template_env=template_env)
        writer.write_string_to_disk(
            database_ddl,
            database_path / f"{database.name}.sql",
        )
        for schema in database.schemas:
            schema_path = database_path / "schemas" / schema.name
            schema_ddl = generate_schema_create_ddl(base_obj=schema, template_env=template_env)
            writer.write_string_to_disk(
                schema_ddl,
                schema_path / f"{schema.name}.sql",
            )
            tables_path = schema_path / "tables"
            for table in schema.tables:
                table_ddl = generate_table_create_ddl(
                    schema_base_obj=schema,
                    table_base_obj=table,
                    template_env=template_env,
                )
                writer.write_string_to_disk(
                    table_ddl,
                    tables_path / f"{table.name}.sql",
                )


def create_script_from_db_model(databases: base.Databases, template_env: jinja2.Environment) -> Any:
    """
    Create DDL from database model.
    """
    script = ""
    for database in databases.databases:
        database_ddl = generate_database_create_ddl(base_obj=database, template_env=template_env)
        script += f"{database_ddl}\n"
        for schema in database.schemas:
            schema_ddl = generate_schema_create_ddl(base_obj=schema, template_env=template_env)
            script += f"{schema_ddl}\n"
            for table in schema.tables:
                table_ddl = generate_table_create_ddl(
                    schema_base_obj=schema,
                    table_base_obj=table,
                    template_env=template_env,
                )
                script += f"{table_ddl}\n"
    return script
