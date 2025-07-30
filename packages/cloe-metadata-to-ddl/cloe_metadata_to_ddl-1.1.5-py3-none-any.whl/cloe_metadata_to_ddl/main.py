import logging
import pathlib
from enum import Enum
from typing import Annotated

import cloe_metadata.utils.writer as writer
import typer
from cloe_metadata import base

from cloe_metadata_to_ddl import utils

logger = logging.getLogger(__name__)

app = typer.Typer()


class DDLOutputMode(str, Enum):
    single = "single"
    multi = "multi"


class OutputSQLSystemType(str, Enum):
    t_sql = "t_sql"
    snowflake_sql = "snowflake_sql"


@app.command()
def write_ddls_to_disk(
    input_model_path: Annotated[
        pathlib.Path,
        typer.Argument(help="Path to the CLOE model."),
    ],
    output_path: Annotated[
        pathlib.Path,
        typer.Argument(
            help="Path to output the scripts.",
        ),
    ],
    output_mode: Annotated[
        DDLOutputMode,
        typer.Option(
            help=(
                "The mode of the DDL creation. The options are 'single' or 'multi'. When"
                " 'single' is selected the output is one file. When 'multi' is slected"
                " the output is multiple files that in a file hierarchy."
            ),
        ),
    ] = DDLOutputMode.single,
    output_sql_system_type: Annotated[
        OutputSQLSystemType,
        typer.Option(
            help="Output sql language.",
        ),
    ] = OutputSQLSystemType.snowflake_sql,
) -> None:
    """
    Creates DDL's for a Snowflake Database model.
    """
    databases, d_errors = base.Databases.read_instances_from_disk(input_model_path)
    if len(d_errors) > 0:
        raise ValueError(
            "The provided models did not pass validation, please run validation.",
        )
    template_env = utils.load_package(output_sql_system_type.value)
    if output_mode == DDLOutputMode.single:
        content = utils.create_script_from_db_model(
            databases=databases, template_env=template_env
        )
        writer.write_string_to_disk(content, output_path / "cloe_ddls.sql")
    else:
        utils.create_model_on_disk_from_db_model(
            output_path=output_path, databases=databases, template_env=template_env
        )
