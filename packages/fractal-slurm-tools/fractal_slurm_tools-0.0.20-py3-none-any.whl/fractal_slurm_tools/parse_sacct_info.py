import logging
from copy import deepcopy
from typing import Any
from typing import Callable

from .run_sacct_command import run_sacct_command
from .sacct_fields import DELIMITER
from .sacct_fields import SACCT_FIELDS
from .sacct_parsers import SACCT_FIELD_PARSERS

logger = logging.getLogger(__name__)

SLURMTaskInfo = dict[str, Any]

INDEX_JOB_NAME = SACCT_FIELDS.index("JobName")
INDEX_STATE = SACCT_FIELDS.index("State")


def parse_sacct_info(
    job_string: str,
    task_subfolder_name: str | None = None,
    parser_overrides: dict[str, Callable] | None = None,
) -> list[SLURMTaskInfo]:
    """
    Run `sacct` and parse its output

    Args:
        job_string:
            Either a single SLURM-job ID or a comma-separated list, which is
            then provided to `sacct` option `-j`.
        task_subfolder_name:
            Name of task subfolder, which is included in the output.
        parser_overrides:
            Overrides of the parser defined in `SACCT_FIELD_PARSERS`

    Returns:
        List of `SLURMTaskInfo` dictionaries (one per `python` line in
        `sacct` output).
    """
    logger.debug(f"START, with {job_string=}.")

    # Update parsers, if needed
    actual_parsers = deepcopy(SACCT_FIELD_PARSERS)
    actual_parsers.update(parser_overrides or {})

    # Run `sacct` command
    stdout = run_sacct_command(job_string=job_string)
    lines = stdout.splitlines()

    list_task_info = []
    for line in lines:
        line_items = line.split(DELIMITER)
        # Skip non-Python steps/tasks
        if "python" not in line_items[INDEX_JOB_NAME]:
            continue
        # Skip running steps
        if line_items[INDEX_STATE] == "RUNNING":
            continue

        # Parse all fields
        try:
            task_info = {
                SACCT_FIELDS[ind]: actual_parsers[SACCT_FIELDS[ind]](item)
                for ind, item in enumerate(line_items)
            }
        except Exception as e:
            logger.error(f"Could not parse {line=}")
            for ind, item in enumerate(line_items):
                logger.error(f"'{SACCT_FIELDS[ind]}' raw item: {item}")
                logger.error(
                    f"'{SACCT_FIELDS[ind]}' parsed item: "
                    f"{actual_parsers[SACCT_FIELDS[ind]](item)}"
                )
            raise e
        if task_subfolder_name is not None:
            task_info.update(dict(task_subfolder=task_subfolder_name))
        list_task_info.append(task_info)
    return list_task_info
