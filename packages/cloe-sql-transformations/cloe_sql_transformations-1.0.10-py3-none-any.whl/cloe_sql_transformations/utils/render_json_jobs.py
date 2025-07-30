import logging
import pathlib
import uuid

from cloe_metadata import base
from cloe_metadata.base.jobs import exec_sql

from cloe_sql_transformations import model

logger = logging.getLogger(__name__)


def json_job_merger(
    jobs: dict[uuid.UUID, exec_sql.ExecSQL],
    existing_jobs: base.Jobs,
) -> base.Jobs:
    all_jobs = []
    existing_sql_jobs: dict[uuid.UUID, exec_sql.ExecSQL] = {}
    for job in existing_jobs.get_jobs().values():
        if isinstance(job, base.ExecSQL):
            existing_sql_jobs[job.id] = job
        else:
            all_jobs.append(job)
    for id, job in jobs.items():
        if id in existing_sql_jobs:
            existing_sql_jobs[id].queries = job.queries
        else:
            existing_sql_jobs[id] = job
    existing_jobs.jobs = all_jobs + list(existing_sql_jobs.values())
    return existing_jobs


def render_json_jobs(
    pipes: list[model.CustomDataflowGenerator | model.DataflowGenerator],
    targettype_to_conversion: dict[str, model.ConversionTemplateGenerator],
    update_existing_exec_sql_jobs: bool,
    input_model_path: pathlib.Path,
) -> base.Jobs:
    """
    Sub entrypoint for to_sql main function for output_mode json.
    """
    if update_existing_exec_sql_jobs:
        existing_jobs, j_errors = base.Jobs.read_instances_from_disk(input_model_path)
        if len(j_errors) > 0:
            raise ValueError(
                "The provided models did not pass validation, please run validation.",
            )
    else:
        existing_jobs = base.Jobs(jobs=[])
    jobs = {}
    for pipe in pipes:
        output_key = pipe.job_id or uuid.uuid4()
        if isinstance(pipe, model.DataflowGenerator):
            query = pipe.gen_exec_sql_query(targettype_to_conversion)
        elif isinstance(pipe, model.CustomDataflowGenerator):
            query = pipe.gen_job()
        else:
            raise ValueError("Unknown job type.")
        exec_job = exec_sql.ExecSQL(
            id=output_key,
            name=pipe.name,
            queries=query,
            connection_id=uuid.UUID(int=0),
        )
        jobs[output_key] = exec_job
    return json_job_merger(jobs, existing_jobs)
