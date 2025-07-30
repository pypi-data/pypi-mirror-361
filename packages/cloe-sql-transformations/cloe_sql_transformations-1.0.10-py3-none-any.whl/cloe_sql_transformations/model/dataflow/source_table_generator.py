import re

import jinja2
from cloe_metadata.shared.modeler import dataflow

from cloe_sql_transformations.model.dataflow.column_mapping_generator import (
    ColumnMappingGenerator,
)
from cloe_sql_transformations.model.dataflow.lookup_generator import LookupGenerator
from cloe_sql_transformations.model.sql_syntax import SQLSyntax


class SourceTableGenerator:
    """
    SourceTable metadata generator class. Supports
    Dataflow class in generating sql snippets.
    """

    def __init__(
        self,
        source_table: dataflow.SourceTable,
        column_mappings: list[dataflow.ColumnMapping],
        sql_syntax: SQLSyntax,
        object_identifier_template: jinja2.Template,
    ) -> None:
        self.table_id = source_table.base_obj.table_id
        self.tenant_id = source_table.base_obj.tenant_id
        self.order_by = source_table.base_obj.order_by
        self.column_mappings = [
            ColumnMappingGenerator(
                i, sql_syntax, object_identifier_template=object_identifier_template
            )
            for i in column_mappings
        ]
        self.is_active = source_table.base_obj.is_active
        self.source_schema, self.source_table = source_table.source_schema_table
        self.tenant = source_table.tenant
        self.sql_syntax = sql_syntax
        self.dq1_prefix = "V_DQ1_"
        self.dq2_prefix = "V_DQ2_"
        self.dq3_prefix = "V_DQ3_"
        self.object_identifier_template = object_identifier_template

    def _gen_bk(self, bk_template: jinja2.Template) -> None:
        enumerated_columns = {
            column.bk_order: self.sql_syntax.column_identifier(
                column.source_column_name
            )
            for column in self.column_mappings
            if column.bk_order is not None and column.source_column_name is not None
        }
        bks = [enumerated_columns[i] for i in sorted(enumerated_columns)]
        if self.tenant is not None:
            self.bk_artifact = bk_template.render(bks=bks, tenant=self.tenant.name)
        else:
            self.bk_artifact = bk_template.render(bks=bks)

    def prep_lookups(self, lookups: list[LookupGenerator]) -> None:
        for lookup in lookups:
            if self.tenant is not None:
                lookup.gen(self.tenant.name)
            else:
                lookup.gen()

    def get_source_table_identifier(self, name_prefix: str | None = None) -> str:
        return self.object_identifier_template.render(
            schema_obj=self.source_schema,
            table_obj=self.source_table,
            name_prefix=name_prefix,
        )

    def gen_dq1_variables(self) -> dict[str, str]:
        variables = {
            "dq1_view_identifier_artifact": self.get_source_table_identifier(
                self.dq1_prefix
            ),
            "dq1_view_source_object_artifact": self.get_source_table_identifier(),
            "bk_artifact": self.bk_artifact,
        }
        return variables

    def gen_dq2_variables(self, include_dq1: bool) -> dict[str, str]:
        dq2_view_source_object_artifact = self.get_source_table_identifier()
        if include_dq1:
            dq2_view_source_object_artifact = self.get_source_table_identifier(
                self.dq1_prefix
            )
        variables = {
            "dq2_view_identifier_artifact": self.get_source_table_identifier(
                self.dq2_prefix
            ),
            "dq2_view_source_object_artifact": dq2_view_source_object_artifact,
        }
        return variables

    def gen_dq1_logging_variables(self) -> dict[str, str]:
        variables = {
            "dq1_view_identifier_artifact": self.get_source_table_identifier(
                self.dq1_prefix
            )
        }
        return variables

    def gen_dq2_logging_variables(self) -> dict[str, str]:
        variables = {
            "dq2_view_identifier_artifact": self.get_source_table_identifier(
                self.dq2_prefix
            )
        }
        return variables

    def gen_dq3_logging_variables(self) -> dict[str, str]:
        variables = {
            "dq3_view_identifier_artifact": self.get_source_table_identifier(
                self.dq3_prefix
            )
        }
        return variables

    def gen_dq3_variables(self, include_dq1: bool, include_dq2: bool) -> dict[str, str]:
        dq3_view_source_object_artifact = self.get_source_table_identifier()
        if include_dq2:
            dq3_view_source_object_artifact = self.get_source_table_identifier(
                self.dq2_prefix
            )
        elif include_dq1:
            dq3_view_source_object_artifact = self.get_source_table_identifier(
                self.dq1_prefix
            )
        variables = {
            "dq3_view_identifier_artifact": self.get_source_table_identifier(
                self.dq3_prefix
            ),
            "dq3_view_source_object_artifact": dq3_view_source_object_artifact,
        }
        return variables

    @staticmethod
    def _clean(statement: str) -> str:
        statement = re.sub(r",\s*,", ", ", statement)
        statement = re.sub(r"\s+;", ";", statement)
        statement = re.sub(r"\n\s+\n", "\n", statement)
        return statement

    def gen(
        self,
        template: jinja2.Template,
        bk_template: jinja2.Template,
        include_dq1: bool,
        include_dq2: bool,
    ) -> str:
        """
        Generates all source_table metadata based
        sql snippets.
        """
        self._gen_bk(bk_template=bk_template)
        source_table_identifier = self.get_source_table_identifier()
        if include_dq2:
            source_table_identifier = self.get_source_table_identifier(self.dq2_prefix)
        elif include_dq1:
            source_table_identifier = self.get_source_table_identifier(self.dq1_prefix)
        anchors = {
            "source_table_identifier_artifact": source_table_identifier,
            "bk_artifact": self.bk_artifact,
        }
        self.statement = template.render(anchors)
        return self._clean(self.statement)
