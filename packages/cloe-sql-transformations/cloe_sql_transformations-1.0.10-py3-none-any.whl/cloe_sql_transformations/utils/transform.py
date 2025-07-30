import jinja2
from cloe_metadata import base
from cloe_metadata.shared.modeler import custom_dataflow, dataflow

from cloe_sql_transformations.model import (
    ConversionTemplateGenerator,
    CustomDataflowGenerator,
    DataflowGenerator,
)
from cloe_sql_transformations.model.sql_syntax import SQLSyntax


def transform_pipes(
    dataflows: list[dataflow.Dataflow],
    custom_dataflows: list[custom_dataflow.CustomDataflow],
    sql_syntax: SQLSyntax,
    object_identifier_template: jinja2.Template,
) -> list[DataflowGenerator | CustomDataflowGenerator]:
    """
    Transform dataflows and custom_dataflows to custom classes.
    """
    trans_pipes: list[DataflowGenerator | CustomDataflowGenerator] = []
    for shared_dataflow in dataflows:
        trans_pipes.append(
            DataflowGenerator(
                shared_dataflow,
                sql_syntax,
                object_identifier_template=object_identifier_template,
            )
        )
    for shared_custom_dataflow in custom_dataflows:
        trans_pipes.append(
            CustomDataflowGenerator(
                shared_custom_dataflow,
                object_identifier_template=object_identifier_template,
            )
        )
    return trans_pipes


def transform_common(
    conversion_templates: base.ConversionTemplates, sql_syntax: SQLSyntax
) -> dict[str, ConversionTemplateGenerator]:
    """Transforms common templates."""
    converted_conversions: dict[str, ConversionTemplateGenerator] = {}
    for k, temp in conversion_templates.get_templates().items():
        if isinstance(temp, base.ConversionTemplate):
            converted_conversions[k] = ConversionTemplateGenerator(temp, sql_syntax)
    return converted_conversions
