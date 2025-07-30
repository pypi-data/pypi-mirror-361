import uuid

from cloe_sql_transformations import model


def render_sql_script(
    pipes: list[model.CustomDataflowGenerator | model.DataflowGenerator],
    targettype_to_conversion: dict[str, model.ConversionTemplateGenerator],
) -> str:
    """
    Sub entrypoint for to_sql main function for output_mode sql_*
    """
    output: dict[uuid.UUID, str] = {}
    for pipe in pipes:
        output_key = pipe.job_id or uuid.uuid4()
        if isinstance(pipe, model.DataflowGenerator):
            output[output_key] = pipe.gen_script(targettype_to_conversion)
        elif isinstance(pipe, model.CustomDataflowGenerator):
            output[output_key] = pipe.gen_script()
    rendered_pipe_queries = ""
    for name, out in output.items():
        rendered_pipe_queries += f"\n\n\n\n--NEXT PIPE STARTING {name}\n{out}"
    return rendered_pipe_queries
