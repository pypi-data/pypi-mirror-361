import copy
import logging
import re

import jinja2
from cloe_metadata import base
from cloe_metadata.base.jobs import exec_sql
from cloe_metadata.shared.modeler import dataflow
from cloe_metadata.utils import templating_engine

from cloe_sql_transformations.model.artifacts import Artifacts, VersionArtifact
from cloe_sql_transformations.model.conversion_template_generator import (
    ConversionTemplateGenerator,
)
from cloe_sql_transformations.model.dataflow.column_mapping_generator import (
    ColumnMappingGenerator,
)
from cloe_sql_transformations.model.dataflow.lookup_generator import LookupGenerator
from cloe_sql_transformations.model.dataflow.source_table_generator import (
    SourceTableGenerator,
)
from cloe_sql_transformations.model.sql_syntax import SQLSyntax
from cloe_sql_transformations.sql.sql_templates import package_loader

logger = logging.getLogger(__name__)


class DataflowGenerator:
    """Dataflow metadata to sql generator class."""

    def __init__(
        self,
        dataflow: dataflow.Dataflow,
        sql_syntax: SQLSyntax,
        object_identifier_template: jinja2.Template,
    ) -> None:
        self.name = dataflow.base_obj.name
        self.job_id = dataflow.base_obj.job_id
        self.sink_table_id = dataflow.base_obj.sink_table_id
        self.sql_template_id = dataflow.base_obj.sql_template_id
        self.include_dq1 = dataflow.base_obj.include_dq1
        self.include_dq2 = dataflow.base_obj.include_dq2
        self.include_dq3 = dataflow.base_obj.include_dq3
        self.log_dq1 = dataflow.base_obj.log_dq1
        self.log_dq2 = dataflow.base_obj.log_dq2
        self.log_dq3 = dataflow.base_obj.log_dq3
        self.template_environment = templating_engine.get_jinja_env(package_loader)
        self.postprocessing_sql = dataflow.base_obj.post_processing_sql
        self.preprocessing_sql = dataflow.base_obj.pre_processing_sql
        self.source_tables = {
            source_table.base_obj.table_id: SourceTableGenerator(
                source_table,
                column_mappings=dataflow.shared_column_mappings,
                sql_syntax=sql_syntax,
                object_identifier_template=object_identifier_template,
            )
            for source_table in dataflow.shared_source_tables
        }
        self.column_mappings = [
            ColumnMappingGenerator(
                i, sql_syntax, object_identifier_template=object_identifier_template
            )
            for i in dataflow.shared_column_mappings
        ]
        self.lookups = []
        self.sink_schema, self.sink_table = dataflow.sink_schema_table
        # This sql template ist mostly a workaround for static type checker.
        # sql_template should never be none.
        self.sql_template = dataflow.sql_template or base.SQLTemplate(
            id=99, name="None", template="TemplateFail"
        )
        self.sql_syntax = sql_syntax
        self.object_identifier_template = object_identifier_template
        self.artifacts = Artifacts(
            sql_syntax=sql_syntax,
            include_dq1=dataflow.base_obj.include_dq1,
            include_dq2=dataflow.base_obj.include_dq2,
            include_dq3=dataflow.base_obj.include_dq3,
            ver_artifacts={
                mapping.table_identifier: VersionArtifact(
                    sql_syntax=sql_syntax,
                    sink_table_identifier=mapping.table_identifier,
                )
                for mapping in self.column_mappings
                if mapping.is_version
            },
        )
        if dataflow.base_obj.lookups:
            self.lookups = [
                LookupGenerator(
                    i,
                    lookup_id=lu_id,
                    sql_syntax=sql_syntax,
                    artifacts=self.artifacts,
                    template_environment=self.template_environment,
                    object_identifier_template=object_identifier_template,
                )
                for lu_id, i in enumerate(dataflow.shared_lookups)
            ]

    @property
    def sink_table_identifier(self) -> str:
        return self.object_identifier_template.render(
            schema_obj=self.sink_schema,
            table_obj=self.sink_table,
        )

    def _gen_rcm_snippets(
        self, id_to_conversion: dict[str, ConversionTemplateGenerator]
    ) -> None:
        """
        Generates column mappings snippets.
        """
        self.artifacts.sink_table_identifier_artifact = self.sink_table_identifier
        for mapping in self.column_mappings:
            mapping.gen_all(
                id_to_conversion,
                self.template_environment.from_string(
                    self.sql_syntax.engine_templates.null_handling
                ),
                self.artifacts,
            )

    def _gen_lookups(self) -> None:
        for lookup in self.lookups:
            lookup.gen_rcm_snippets()

    @staticmethod
    def _render_name_template(dq_view_ddl: str) -> str:
        try:
            dq_view_template = jinja2.Template(dq_view_ddl)
            return dq_view_template.render()
        except jinja2.TemplateSyntaxError:
            logger.debug("DQ view is no valid jinja2 template. Will be used as is.")
            return dq_view_ddl

    def gen_dq_views_json(self) -> list[dict[str, str | int]]:
        dq_views: list[dict[str, str | int]] = []
        template_dq1_view = self.template_environment.from_string(
            self.sql_syntax.engine_templates.dq1_view_ddl
        )
        template_dq2_view = self.template_environment.from_string(
            self.sql_syntax.engine_templates.dq2_view_ddl
        )
        template_dq3_view = self.template_environment.from_string(
            self.sql_syntax.engine_templates.dq3_view_ddl
        )
        for table_id, table in self.source_tables.items():
            if self.include_dq1:
                dq_views.append(
                    {
                        "id": str(table_id),
                        "level": 1,
                        "content": template_dq1_view.render(
                            **table.gen_dq1_variables()
                        ),
                    }
                )
            if self.include_dq2:
                dq_views.append(
                    {
                        "id": str(table_id),
                        "level": 2,
                        "content": template_dq2_view.render(
                            **table.gen_dq2_variables(self.include_dq1)
                        ),
                    }
                )
            if self.include_dq3:
                dq_views.append(
                    {
                        "id": str(table_id),
                        "level": 3,
                        "content": template_dq3_view.render(
                            **table.gen_dq3_variables(
                                self.include_dq1, self.include_dq2
                            )
                        ),
                    }
                )
        return dq_views

    def gen_dq_views(self, sql_transaction_separator: str = "") -> dict[str, str]:
        """
        Generates data quality views DDLs.
        """
        dq_view = {}
        template_dq1_view = self.template_environment.from_string(
            self.sql_syntax.engine_templates.dq1_view_ddl
        )
        template_dq2_view = self.template_environment.from_string(
            self.sql_syntax.engine_templates.dq2_view_ddl
        )
        template_dq3_view = self.template_environment.from_string(
            self.sql_syntax.engine_templates.dq3_view_ddl
        )
        for table_id, table in self.source_tables.items():
            if self.include_dq1:
                dq_view[f"{self.name}_{table_id}_dq1"] = template_dq1_view.render(
                    **table.gen_dq1_variables()
                )
            if self.include_dq2:
                dq_view[f"{self.name}_{table_id}_dq2"] = template_dq2_view.render(
                    **table.gen_dq2_variables(self.include_dq1)
                )
            if self.include_dq3:
                dq_view[f"{self.name}_{table_id}_dq3"] = template_dq3_view.render(
                    **table.gen_dq3_variables(self.include_dq1, self.include_dq2)
                )
        for key, view in dq_view.items():
            dq_view[key] = (
                f"{self._render_name_template(view)}{sql_transaction_separator}\n"
            )
        return dq_view

    def _gen_dq_logging(self, table: SourceTableGenerator) -> str:
        template_dq1_log = self.template_environment.from_string(
            self.sql_syntax.engine_templates.dq1_error_logging
        )
        template_dq2_log = self.template_environment.from_string(
            self.sql_syntax.engine_templates.dq2_error_logging
        )
        template_dq3_log = self.template_environment.from_string(
            self.sql_syntax.engine_templates.dq3_error_logging
        )
        logging_queries = ""
        if self.include_dq1 and self.log_dq1:
            rendered_dq1 = template_dq1_log.render(**table.gen_dq1_logging_variables())
            logging_queries += f"\n{rendered_dq1}"
        if self.include_dq2 and self.log_dq2:
            rendered_dq2 = template_dq2_log.render(**table.gen_dq2_logging_variables())
            logging_queries += f"\n{rendered_dq2}"
        if self.log_dq3:
            rendered_dq3 = template_dq3_log.render(**table.gen_dq3_logging_variables())
            logging_queries += f"\n{rendered_dq3}"
        return logging_queries

    def _gen_sql_script(self) -> str:
        template = self.template_environment.from_string(self.sql_template.template)
        queries = {}
        enumerated_tables = [
            self.source_tables[i]
            for i in sorted(
                self.source_tables,
                key=lambda table_id: self.source_tables[table_id].order_by,
            )
        ]
        bk_template = self.template_environment.from_string(
            self.sql_syntax.engine_templates.bk_generation
        )
        for table in enumerated_tables:
            frozen_artifacts = copy.deepcopy(self.artifacts)
            if self.lookups:
                table.prep_lookups(self.lookups)
            self.template_environment.globals |= self.artifacts.finalize_environment()
            queries[table.order_by] = table.gen(
                template=template,
                bk_template=bk_template,
                include_dq1=self.include_dq1,
                include_dq2=self.include_dq2,
            )
            queries[table.order_by] += self._gen_dq_logging(table)
            self.artifacts = frozen_artifacts
            if self.lookups:
                for lookup in self.lookups:
                    lookup.artifacts = frozen_artifacts
        query_block = "\n\n-- NEXT TABLE STARTING \n".join(
            [queries[i] for i in sorted(queries)]
        )
        return (
            f"\n\n{self.preprocessing_sql or ''}{query_block}"
            f"\n\n{self.postprocessing_sql or ''}"
        )

    def _gen_exec_sql_job(self) -> list[exec_sql.Query]:
        template = self.template_environment.from_string(self.sql_template.template)
        enumerated_tables = [
            self.source_tables[i]
            for i in sorted(
                self.source_tables,
                key=lambda table_id: self.source_tables[table_id].order_by,
            )
        ]
        bk_template = self.template_environment.from_string(
            self.sql_syntax.engine_templates.bk_generation
        )
        queries: list[exec_sql.Query] = []
        exec_order_numbers = []
        for table in enumerated_tables:
            frozen_artifacts = copy.deepcopy(self.artifacts)
            if self.lookups:
                table.prep_lookups(self.lookups)
            self.template_environment.globals |= self.artifacts.finalize_environment()
            exec_order_numbers.append(table.order_by)
            source_identifier = table.get_source_table_identifier()
            sink_identifier = self.sink_table_identifier
            runtime_query = table.gen(
                template=template,
                bk_template=bk_template,
                include_dq1=self.include_dq1,
                include_dq2=self.include_dq2,
            )
            runtime_query += self._gen_dq_logging(table)
            split_queries = [
                sub_query.strip()
                for sub_query in runtime_query.split(";")
                if sub_query is not None and len(re.sub(r"\s", "", sub_query)) > 1
            ]
            split_queries = split_queries if len(split_queries) > 1 else [runtime_query]
            for order_number, query in enumerate(split_queries):
                exec_sql_query = exec_sql.Query(
                    query=query,
                    exec_order=int(f"{table.order_by}{order_number}"),
                    description=f"{source_identifier} TO {sink_identifier}",
                )
                queries.append(exec_sql_query)
            self.artifacts = frozen_artifacts
            if self.lookups:
                for lookup in self.lookups:
                    lookup.artifacts = frozen_artifacts
        if self.preprocessing_sql:
            exec_sql_query = exec_sql.Query(
                query=self.preprocessing_sql,
                exec_order=min(exec_order_numbers) - 1,
                description="Preprocessing",
            )
            queries.append(exec_sql_query)
        if self.postprocessing_sql:
            exec_sql_query = exec_sql.Query(
                query=self.postprocessing_sql,
                exec_order=max(exec_order_numbers) + 1,
                description="Postprocessing",
            )
            queries.append(exec_sql_query)
        return queries

    def _gen(
        self,
        id_to_conversion: dict[str, ConversionTemplateGenerator],
    ) -> None:
        self._gen_rcm_snippets(id_to_conversion)
        self._gen_lookups()

    def gen_script(
        self,
        id_to_conversion: dict[str, ConversionTemplateGenerator],
    ) -> str:
        """
        Generates a sql script.
        """
        self._gen(id_to_conversion)
        return self._gen_sql_script()

    def gen_exec_sql_query(
        self,
        id_to_conversion: dict[str, ConversionTemplateGenerator],
    ) -> list[exec_sql.Query]:
        """
        Generates an exec_sql job json.
        """
        self._gen(id_to_conversion)
        return self._gen_exec_sql_job()
