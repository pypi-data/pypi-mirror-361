import jinja2
from cloe_metadata.base import ConversionTemplate

from cloe_sql_transformations.model.sql_syntax import SQLSyntax


class ConversionTemplateGenerator:
    """
    Base class for working with conversion templates
    in the to_sql module.
    """

    def __init__(
        self, conversion_template: ConversionTemplate, sql_syntax: SQLSyntax
    ) -> None:
        self.output_type = conversion_template.output_type
        self.convert_template = jinja2.Template(conversion_template.convert_template)
        self.on_convert_error_default_value = (
            conversion_template.on_convert_error_default_value
        )
        self.sql_syntax = sql_syntax

    def get_conversion_function_string(self, column_name: str) -> str:
        return self.convert_template.render(column_name=column_name, include_dq2=False)

    def get_dq_function_string(
        self,
        column_name: str,
        error_handling: bool,
        null_check_template: jinja2.Template,
        error_handling_value: str | None = None,
    ) -> str:
        dq_function = self.convert_template.render(
            column_name=column_name, include_dq2=True
        )
        if error_handling:
            return self.sql_syntax.column_nullhandling(
                dq_function,
                null_check_template,
                error_handling_value or self.on_convert_error_default_value,
            )
        return dq_function
