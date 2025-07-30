import jinja2
from cloe_metadata.shared.modeler import dataflow

from cloe_sql_transformations.model.artifacts import Artifacts
from cloe_sql_transformations.model.conversion_template_generator import (
    ConversionTemplateGenerator,
)
from cloe_sql_transformations.model.sql_syntax import SQLSyntax


class ColumnMappingGenerator:
    """Generates and controls dataflow column level snippet generation."""

    def __init__(
        self,
        column_mapping: dataflow.ColumnMapping,
        sql_syntax: SQLSyntax,
        object_identifier_template: jinja2.Template,
    ) -> None:
        self.bk_order = column_mapping.base_obj.bk_order
        self.sink_table_id = column_mapping.base_obj.sink_table_id
        self.source_column_name = column_mapping.base_obj.source_column_name
        self._sink_column_name = column_mapping.base_obj.sink_column_name
        self.calculation = column_mapping.base_obj.calculation
        self.convert_to_datatype = column_mapping.base_obj.convert_to_datatype
        self.is_insert = column_mapping.base_obj.is_insert
        self.is_update = column_mapping.base_obj.is_update
        self.is_load_on_convert_error = column_mapping.base_obj.is_load_on_convert_error
        self.is_logging_on_convert_error = (
            column_mapping.base_obj.is_logging_on_convert_error
        )
        self.on_convert_error_value = column_mapping.base_obj.on_convert_error_value
        self.on_null_value = column_mapping.base_obj.on_null_value
        self.sink_schema, self.sink_table = column_mapping.sink_schema_table
        self.sql_syntax = sql_syntax
        self.null_check_template: jinja2.Template
        self.conv_template: ConversionTemplateGenerator
        self.dq_on: bool = False
        self.object_identifier_template = object_identifier_template

    @property
    def source_column_identifier(self) -> str:
        if self.source_column_name is not None:
            return f"s.{self.sql_syntax.column_identifier(self.source_column_name)}"
        raise ValueError("source_column_name is not set.")

    @property
    def sink_column_name(self) -> str:
        if self._sink_column_name is not None:
            return self.sql_syntax.column_identifier(self._sink_column_name)
        raise ValueError("_sink_column_name is not set.")

    @property
    def sink_column_identifier(self) -> str:
        name = self.sink_column_name
        if self.sink_table is not None and self.sink_table.is_version:
            return f"ver.{name}"
        return f"t.{name}"

    @property
    def is_bk_only(self) -> bool:
        return (self.bk_order is not None) and (self._sink_column_name is None)

    @property
    def table_identifier(self) -> str:
        return self.object_identifier_template.render(
            schema_obj=self.sink_schema,
            table_obj=self.sink_table,
        )

    @property
    def is_version(self) -> bool:
        if self.sink_table is not None and self.sink_table.is_version:
            return True
        return False

    def _get_column_base(
        self, prioritize_name: bool | None = None, with_alias: bool = False
    ) -> str:
        """
        Generates the column that need to be used by all methods which reference the
        "raw" column. If there is no calculation set it always return the column name
        with a table alias. If a calculation is specified it will either return the
        calculation with a column alias or the raw calculation.
        """
        prioritize_name = prioritize_name or self.dq_on
        if (
            self.calculation is not None
            and self.source_column_name is not None
            and with_alias
        ):
            return self.sql_syntax.column_alias(
                self.calculation,
                self.sql_syntax.column_identifier(self.source_column_name),
            )
        if self.calculation is None or prioritize_name:
            return self.source_column_identifier
        return self.calculation

    def _get_null_check(self, prioritize_name: bool) -> str:
        """
        Generates a null check snippet. It compares it checks
        both the sink and source column for null values and wraps them
        in an "and" logic check.
        """
        return self.sql_syntax.condition_comparison_and(
            self.sql_syntax.column_is_null(self.sink_column_identifier),
            self.sql_syntax.column_is_null(
                self._get_column_base(prioritize_name), is_not=True
            ),
            with_brackets=True,
        )

    def _get_on_null(self, prioritize_calculation: bool | None = None) -> str:
        """
        Generates a column null handling snippet if null handling is set for this
        column. Snippet will include alternative value if column level is null.
        """
        if self.on_null_value and prioritize_calculation is None:
            return self.sql_syntax.column_nullhandling(
                column_name=self._get_column_base(),
                null_check_template=self.null_check_template,
                alternative_value=self.on_null_value,
            )
        if self.on_null_value and prioritize_calculation is True:
            return self.sql_syntax.column_nullhandling(
                column_name=self._get_column_base(prioritize_name=False),
                null_check_template=self.null_check_template,
                alternative_value=self.on_null_value,
            )
        return self._get_column_base(prioritize_name=prioritize_calculation)

    def _get_dq_handling(
        self, error_handling: bool, prioritize_calculation: bool = True
    ) -> str:
        """
        Generates a data quality conversion snippet. The snippet will include
        transformation of the column to the target datatype based on the model
        including error_handling.
        """
        return self.sql_syntax.case_when(
            self.sql_syntax.column_is_null(self._get_column_base()),
            self._get_on_null(),
            self.conv_template.get_dq_function_string(
                self._get_on_null(prioritize_calculation),
                null_check_template=self.null_check_template,
                error_handling=error_handling,
                error_handling_value=self.on_convert_error_value,
            ),
        )

    def _gen_dq2_w_conversion_snippets(self) -> None:
        """Generates all column level data quality 2 snippets."""
        dq2_source_column_artifact = self._get_dq_handling(
            self.is_load_on_convert_error
        )
        column_compare_dq2_artifact = self.sql_syntax.column_comparison_difference(
            self.sink_column_identifier, dq2_source_column_artifact
        )
        if self.is_insert and not self.is_version:
            self.template_artifacts.source_insert.append(dq2_source_column_artifact)
        if self.is_update and not self.is_bk_only and not self.is_version:
            self.template_artifacts.sink_source_update.append(
                self.sql_syntax.column_comparison_equality(
                    self.sink_column_name, dq2_source_column_artifact
                )
            )
            self.template_artifacts.sink_source_field_comparison.append(
                self.sql_syntax.condition_comparison_or(
                    column_compare_dq2_artifact,
                    self._get_null_check(self.template_artifacts.include_dq1),
                    with_brackets=True,
                )
            )
        if self.is_version:
            self.template_artifacts.versioning_artifacts[
                self.table_identifier
            ].ver_source_insert.append(dq2_source_column_artifact)
            if self.is_update:
                self.template_artifacts.versioning_artifacts[
                    self.table_identifier
                ].ver_sink_source_field_comparison.append(
                    self.sql_syntax.condition_comparison_or(
                        column_compare_dq2_artifact,
                        self._get_null_check(self.template_artifacts.include_dq1),
                        with_brackets=True,
                    )
                )
        if self.is_logging_on_convert_error:
            self.template_artifacts.dq2_log_where.append(
                self.sql_syntax.condition_comparison_and(
                    self.sql_syntax.column_is_null(self._get_dq_handling(False)),
                    self.sql_syntax.column_is_null(self._get_on_null(), is_not=True),
                    with_brackets=True,
                )
            )
            self.template_artifacts.dq2_log_select.append(self.source_column_identifier)
        if not self.is_load_on_convert_error:
            self.template_artifacts.dq2_view_where.append(
                self.sql_syntax.condition_comparison_and(
                    self.sql_syntax.column_is_null(
                        self._get_dq_handling(
                            False, not self.template_artifacts.include_dq1
                        )
                    ),
                    self.sql_syntax.column_is_null(
                        self._get_on_null(not self.template_artifacts.include_dq1),
                        is_not=True,
                    ),
                    with_brackets=True,
                )
            )

    def _gen_dq_snippets(self) -> None:
        """Generates data quality snippets for dq views and calls
        _gen_dq2_w_conversion_snippets if sink_column_name is set.
        """
        self.template_artifacts.dq1_log_select.append(self.source_column_identifier)
        self.template_artifacts.dq1_view_select_as_raw.append(
            self._get_column_base(with_alias=True)
        )
        self.template_artifacts.dq2_view_select_as_raw.append(
            self._get_column_base(with_alias=not self.template_artifacts.include_dq1)
        )
        self.template_artifacts.dq3_view_select_as_raw.append(
            self._get_column_base(
                with_alias=not (
                    self.template_artifacts.include_dq1
                    or self.template_artifacts.include_dq2
                )
            )
        )
        self.template_artifacts.dq1_view_select_as_name.append(self._get_column_base())
        self.template_artifacts.dq2_view_select_as_name.append(self._get_column_base())
        self.template_artifacts.dq3_view_select_as_name.append(self._get_column_base())
        if (
            self.convert_to_datatype is not None
            and self.template_artifacts.include_dq2
            and not self.is_bk_only
        ):
            self._gen_dq2_w_conversion_snippets()

    def _gen_base_w_conversion_snippets(self) -> None:
        """Generates basic column snippets for conversion."""
        conversion_artifact = self.conv_template.get_conversion_function_string(
            self._get_on_null()
        )
        if self.is_insert and not self.is_version:
            self.template_artifacts.source_insert.append(conversion_artifact)
        if self.is_update and not self.is_bk_only and not self.is_version:
            self.template_artifacts.sink_source_update.append(
                self.sql_syntax.column_comparison_equality(
                    self.sink_column_name, conversion_artifact
                )
            )
        column_compare_artifact = self.sql_syntax.column_comparison_difference(
            self.sink_column_identifier, conversion_artifact
        )
        if self.is_version:
            self.template_artifacts.versioning_artifacts[
                self.table_identifier
            ].ver_source_insert.append(conversion_artifact)
            if self.is_update:
                self.template_artifacts.versioning_artifacts[
                    self.table_identifier
                ].ver_sink_source_field_comparison.append(
                    self.sql_syntax.condition_comparison_or(
                        column_compare_artifact,
                        self._get_null_check(self.dq_on),
                        with_brackets=True,
                    )
                )
        self.template_artifacts.sink_source_field_comparison.append(
            self.sql_syntax.condition_comparison_or(
                column_compare_artifact,
                self._get_null_check(self.dq_on),
                with_brackets=True,
            )
        )

    def _gen_base_wo_conversion_snippets(self) -> None:
        """Generates basic column snippets without conversion."""
        if self.is_insert and not self.is_version:
            self.template_artifacts.source_insert.append(self._get_on_null())
        if self.is_update and not self.is_bk_only and not self.is_version:
            self.template_artifacts.sink_source_update.append(
                self.sql_syntax.column_comparison_equality(
                    self.sink_column_name, self._get_on_null()
                )
            )
        column_compare_artifact = self.sql_syntax.column_comparison_difference(
            self.sink_column_identifier, self._get_on_null()
        )
        self.dq_on = (
            self.template_artifacts.include_dq1 or self.template_artifacts.include_dq2
        )
        if self.is_version:
            self.template_artifacts.versioning_artifacts[
                self.table_identifier
            ].ver_source_insert.append(self._get_on_null())
            if self.is_update:
                self.template_artifacts.versioning_artifacts[
                    self.table_identifier
                ].ver_sink_source_field_comparison.append(
                    self.sql_syntax.condition_comparison_or(
                        column_compare_artifact,
                        self._get_null_check(self.dq_on),
                        with_brackets=True,
                    )
                )
        else:
            self.template_artifacts.sink_source_field_comparison.append(
                self.sql_syntax.condition_comparison_or(
                    column_compare_artifact,
                    self._get_null_check(self.dq_on),
                    with_brackets=True,
                )
            )

    def gen_base_snippets(self) -> None:
        """Generates sink column snippets and functions as a wrapper around
        non data quality generation functions. Also checks if conversions is set
        calling _gen_base_wo_conversion_snippets or _gen_base_w_conversion_snippets if
        conversion is set and data quality 2 is off.
        """
        if self.is_insert and not self.is_version:
            self.template_artifacts.sink_insert.append(self.sink_column_name)
        elif self.is_version:
            self.template_artifacts.versioning_artifacts[
                self.table_identifier
            ].ver_sink_insert.append(self.sink_column_name)
        if self.convert_to_datatype is None:
            self._gen_base_wo_conversion_snippets()
        elif not self.template_artifacts.include_dq2:
            self._gen_base_w_conversion_snippets()

    def gen_all(
        self,
        id_to_conversion: dict[str, ConversionTemplateGenerator],
        null_check_template: jinja2.Template,
        template_artifacts: Artifacts,
    ) -> None:
        """Main entry method for generating all snippets of column mapping
        and add them to the template global environment.
        """
        self.template_artifacts = template_artifacts
        self.dq_on = (
            self.template_artifacts.include_dq1 or self.template_artifacts.include_dq2
        )
        if self.convert_to_datatype is not None:
            self.conv_template = id_to_conversion[self.convert_to_datatype]
        self.null_check_template = null_check_template
        if self.dq_on and not self.is_version:
            self.template_artifacts.source_lu_used_columns.append(
                self._get_column_base()
            )
        elif not self.is_version:
            self.template_artifacts.source_lu_used_columns.append(
                self._get_column_base(prioritize_name=False)
            )
        if not self.is_bk_only:
            self.gen_base_snippets()
        self._gen_dq_snippets()
