import cloe_metadata.shared.modeler.custom_dataflow as shared_custom_dataflow
import jinja2
from cloe_metadata.base.jobs import exec_sql


class CustomDataflowGenerator:
    """CustomDataflow metadata to sql generator class."""

    def __init__(
        self,
        custom_dataflow: shared_custom_dataflow.CustomDataflow,
        object_identifier_template: jinja2.Template,
    ) -> None:
        self.shared_obj = custom_dataflow
        self.object_identifier_template = object_identifier_template
        self.name = custom_dataflow.base_obj.name
        self.job_id = custom_dataflow.base_obj.job_id
        self.sql_pipe_template: jinja2.Template = jinja2.Template(
            custom_dataflow.base_obj.sql_pipe_template
        )
        self.table_mapping: list[shared_custom_dataflow.TableMapping] = (
            custom_dataflow.shared_table_mappings
        )

    def _gen(self, mapping: shared_custom_dataflow.TableMapping) -> str:
        source_schema, source_table = mapping.source_schema_table
        sink_schema, sink_table = mapping.sink_schema_table
        source_table_identifier = self.object_identifier_template.render(
            schema_obj=source_schema,
            table_obj=source_table,
        )
        sink_table_identifier = self.object_identifier_template.render(
            schema_obj=sink_schema,
            table_obj=sink_table,
        )
        anchors = {
            "source_table": source_table_identifier,
            "sink_table": sink_table_identifier,
        }
        template = self.sql_pipe_template.render(anchors)
        return template

    def gen_script(self) -> str:
        """
        Generates a sql script or exec_sql job json snippet.
        """
        queries = {}
        for mapping in self.table_mapping:
            queries[mapping.base_obj.order_by] = self._gen(mapping)
        return "\n\n-- NEXT TABLE STARTING \n".join(
            [queries[i] for i in sorted(queries)]
        )

    def gen_job(self) -> list[exec_sql.Query]:
        """
        Generates a sql script or exec_sql job json snippet.
        """
        queries = []
        for mapping in self.table_mapping:
            source_schema, source_table = mapping.source_schema_table
            sink_schema, sink_table = mapping.sink_schema_table
            source_table_identifier = self.object_identifier_template.render(
                schema_obj=source_schema,
                table_obj=source_table,
            )
            sink_table_identifier = self.object_identifier_template.render(
                schema_obj=sink_schema,
                table_obj=sink_table,
            )
            source_identifier = source_table_identifier
            sink_identifier = sink_table_identifier
            runtime_query = self._gen(mapping)
            split_queries = [
                sub_query.strip()
                for sub_query in runtime_query.split(";")
                if sub_query is not None and len(sub_query) > 1
            ]
            split_queries = split_queries if len(split_queries) > 1 else [runtime_query]
            for order_number, query in enumerate(split_queries):
                exec_sql_query = exec_sql.Query(
                    query=query,
                    exec_order=int(f"{order_number}{mapping.base_obj.order_by}"),
                    description=f"{source_identifier} TO {sink_identifier}",
                )
                queries.append(exec_sql_query)
        return queries
