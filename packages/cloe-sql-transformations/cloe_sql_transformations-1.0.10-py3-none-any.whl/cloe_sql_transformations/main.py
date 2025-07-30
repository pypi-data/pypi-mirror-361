import logging
import pathlib
from enum import Enum
from typing import Annotated

import cloe_metadata.utils.writer as writer
import jinja2
import typer

from cloe_sql_transformations.model.sql_syntax import SQLSyntax
from cloe_sql_transformations.utils import (
    deploy_dq_views,
    load_models,
    render_json_jobs,
    render_sql_script,
    transform,
)
from cloe_sql_transformations.utils import engine_templates as utils_engine_templates

logger = logging.getLogger(__name__)

app = typer.Typer()


class OutputMode(str, Enum):
    sql = "sql"
    json = "json"


class OutputSQLSystemType(str, Enum):
    t_sql = "t_sql"
    snowflake_sql = "snowflake_sql"


@app.command()
def build(
    input_model_path: Annotated[
        pathlib.Path,
        typer.Argument(help="Path to the CLOE model."),
    ],
    output_path: Annotated[
        pathlib.Path,
        typer.Argument(
            help="Path to output the scripts/jsons.",
        ),
    ],
    output_mode: Annotated[
        OutputMode,
        typer.Option(
            help=(
                "The outputs modes configures if one file per pipe is written to"
                " just one big file(sql) with all pipes"
                " or a exec_job json (json)."
            ),
        ),
    ] = OutputMode.json,
    output_sql_system_type: Annotated[
        OutputSQLSystemType,
        typer.Option(
            help="Output sql language.",
        ),
    ] = OutputSQLSystemType.snowflake_sql,
    update_existing_exec_sql_jobs: Annotated[
        bool,
        typer.Option(
            help="Update existing jobs.",
        ),
    ] = False,
) -> None:
    """
    Main entry for deploying to sql modeler.
    """
    (
        trans_dataflows,
        trans_custom_dataflows,
        sql_templates,
        conversion_templates,
    ) = load_models.load_models(input_model_path)
    if output_sql_system_type == OutputSQLSystemType.t_sql:
        template_package = OutputSQLSystemType.t_sql
        output_sql_transaction_separator = ";\nGO"
    elif output_sql_system_type == OutputSQLSystemType.snowflake_sql:
        template_package = OutputSQLSystemType.snowflake_sql
        output_sql_transaction_separator = ";\n"
    else:
        logger.error("Unknown OutputSQLSystemType %s", OutputSQLSystemType)
        raise ValueError("Unknown OutputSQLSystemType")
    engine_templates = utils_engine_templates.EngineTemplates(template_package.value)
    engine_templates.merge_custom_templates(sql_templates)
    sql_syntax = SQLSyntax(
        engine_templates,
        is_tsql=output_sql_system_type == OutputSQLSystemType.t_sql,
        is_snowflake=output_sql_system_type == OutputSQLSystemType.snowflake_sql,
    )
    trans_pipes = transform.transform_pipes(
        trans_dataflows,
        trans_custom_dataflows,
        sql_syntax,
        object_identifier_template=jinja2.Template(engine_templates.object_identifier),
    )
    trans_targettype_to_conversion = transform.transform_common(
        conversion_templates, sql_syntax
    )
    if output_mode == OutputMode.sql:
        content = render_sql_script.render_sql_script(
            trans_pipes,
            trans_targettype_to_conversion,
        )
        content_output_path = output_path / "rendered_pipe_queries.sql"
        writer.write_string_to_disk(content, content_output_path)
    else:
        exec_sql_jobs = render_json_jobs.render_json_jobs(
            trans_pipes,
            trans_targettype_to_conversion,
            update_existing_exec_sql_jobs,
            input_model_path=input_model_path,
        )
        exec_sql_jobs.write_to_disk(output_path=output_path)
    deploy_dq_views.deploy_dq_views(
        trans_pipes, output_path, output_sql_transaction_separator
    )
