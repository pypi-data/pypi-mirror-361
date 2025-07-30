from jinja2 import Template

from cloe_sql_transformations.utils import engine_templates


class SQLSyntax:
    """
    Config class for various sql templates and keywords.
    """

    def __init__(
        self,
        engine_templates: engine_templates.EngineTemplates,
        is_tsql: bool,
        is_snowflake: bool,
    ) -> None:
        self.engine_templates = engine_templates
        self.select_column_separator = ",\n\t"
        self.where_condition_or = " OR\n\t"
        self.where_condition_and = " AND\n\t"
        self.null_indicator = "NULL"
        self.not_indicator = "NOT"
        self.join_separator = "\n\t"
        self.query_separator = " ;"
        self.statement_separator = " GO "
        self.is_tsql = is_tsql
        self.is_snowflake = is_snowflake

    def column_nullhandling(
        self,
        column_name: str,
        null_check_template: Template,
        alternative_value: str | None = None,
    ) -> str:
        if alternative_value:
            return null_check_template.render(
                column_name=column_name, alternative_value=alternative_value
            )
        return null_check_template.render(column_name=column_name)

    def column_identifier(
        self,
        column_name: str,
    ) -> str:
        if self.is_tsql:
            return f"[{column_name}]"
        if self.is_snowflake:
            return f'"{column_name}"'
        return f"{column_name}"

    @staticmethod
    def combine_columns(column_names: list[str]) -> str:
        return ",\n\t".join(column_names)

    @staticmethod
    def combine_conditions_or(conditions: list[str]) -> str:
        return " OR\n\t".join(conditions)

    @staticmethod
    def column_comparison_equality(
        column_left_name: str, column_right_name: str
    ) -> str:
        return f"{column_left_name} = {column_right_name}"

    @staticmethod
    def column_comparison_difference(
        column_left_name: str, column_right_name: str
    ) -> str:
        return f"{column_left_name} <> {column_right_name}"

    @staticmethod
    def condition_comparison_and(
        condition_left: str, condition_right: str, with_brackets: bool = False
    ) -> str:
        comparison = f"{condition_left} AND {condition_right}"
        if with_brackets:
            comparison = f"({comparison})"
        return comparison

    @staticmethod
    def condition_comparison_or(
        condition_left: str, condition_right: str, with_brackets: bool = False
    ) -> str:
        comparison = f"{condition_left} OR {condition_right}"
        if with_brackets:
            comparison = f"({comparison})"
        return comparison

    @staticmethod
    def column_is_null(column_name: str, is_not: bool = False) -> str:
        if is_not:
            return f"{column_name} IS NOT NULL"
        return f"{column_name} IS NULL"

    @staticmethod
    def column_alias(column_name: str, alias: str) -> str:
        return f"{column_name} AS {alias}"

    @staticmethod
    def case_when(condition: str, true_value: str, false_value: str) -> str:
        return f"CASE WHEN {condition} THEN {true_value} ELSE {false_value} END"
