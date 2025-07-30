import pathlib

import cloe_metadata.utils.writer as writer

from cloe_sql_transformations import model


def deploy_dq_views(
    pipes: list[model.CustomDataflowGenerator | model.DataflowGenerator],
    output_path: pathlib.Path,
    output_sql_transaction_separator: str,
) -> None:
    dq_views: dict[str, str] = {}
    for pipe in pipes:
        if isinstance(pipe, model.DataflowGenerator):
            dq_views |= pipe.gen_dq_views(output_sql_transaction_separator)
    complete_file = ""
    for dq_key, out in dq_views.items():
        complete_file += f"\n\n\n\n--NEXT Table STARTING {dq_key}\n{out}"
    writer.write_string_to_disk(complete_file, output_path / "dq_view_ddls.sql")
