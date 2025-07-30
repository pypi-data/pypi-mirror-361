import logging

from cloe_metadata.shared import jobs

from cloe_metadata_to_ddl.utils import create_ddl_from_exec_sql as create_exec

logger = logging.getLogger(__name__)


def create_stored_procedure_script(
    jobs: list[jobs.ExecSQL],
    is_transaction: bool,
    use_monitoring: bool,
) -> dict[str, str]:
    proc_per_source: dict[str, str] = {}
    for job in jobs:
        if job.sink_connection.get_short_id() in proc_per_source:
            proc_per_source[
                job.sink_connection.get_short_id()
            ] += create_exec.get_procedure_create(job, is_transaction, use_monitoring)
        else:
            proc_per_source[
                job.sink_connection.get_short_id()
            ] = create_exec.get_procedure_create(job, is_transaction, use_monitoring)
        logger.debug("%s created", job.get_procedure_name())
    return proc_per_source
