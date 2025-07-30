import datetime
import uuid
from collections.abc import Callable, Collection
from pathlib import Path
from typing import Any

from rra_tools.shell_tools import mkdir


def get_jobmon_tool(workflow_name: str):  # type: ignore[no-untyped-def]
    """Get a jobmon tool for a given workflow name with a helpful error message.

    Parameters
    ----------
    workflow_name
        The name of the workflow.

    Returns
    -------
    Tool
        A jobmon tool.

    Raises
    ------
    ModuleNotFoundError
        If jobmon is not installed.
    """
    try:
        from jobmon.client.tool import Tool  # type: ignore[import-not-found]
    except ModuleNotFoundError as e:
        msg = (
            "Jobmon is not installed.\n"
            "Ensure you have a file in your home "
            "directory at '~/.pip/pip.conf' with contents\n\n"
            "[global]\n"
            "extra-index-url = https://artifactory.ihme.washington.edu/artifactory/api/pypi/pypi-shared/simple\n"
            "trusted-host = artifactory.ihme.washington.edu/artifactory/api/pypi/pypi-shared\n\n"
            "and run 'pip install jobmon_installer_ihme' to install jobmon."
        )
        raise ModuleNotFoundError(msg) from e

    return Tool(workflow_name)


def _process_args(
    args: dict[str, Collection[Any] | Any] | None,
) -> tuple[dict[str, Collection[Any]], str]:
    """Process arguments for a task.

    Parameters
    ----------
    args
        The arguments to process.

    Returns
    -------
    tuple[dict[str, Collection[Any]], str]
        The names of all non-flag and non-count arguments and the string
        representation of the arguments.
    """
    if args is None:
        return {}, ""
    out_args = {}
    arg_parts = []
    for k, v in args.items():
        if v is not None:
            arg_parts.append(f"--{k} {{{k.replace('-', '_')}}}")
            out_args[k.replace("-", "_")] = v
        elif len(k) == 1 or k in ["v", "vv", "vvv"]:
            arg_parts.append(f"-{k}")
        else:
            arg_parts.append(f"--{k}")
    arg_string = " ".join(arg_parts)
    return out_args, arg_string


def build_parallel_task_graph(  # type: ignore[no-untyped-def] # noqa: PLR0913
    jobmon_tool,
    runner: str,
    task_name: str,
    task_resources: dict[str, str | int],
    *,
    node_args: dict[str, Collection[Any] | None] | None = None,
    flat_node_args: tuple[tuple[str, ...], Collection[tuple[Any, ...]]] | None = None,
    task_args: dict[str, Any] | None = None,
    op_args: dict[str, Any] | None = None,
    max_attempts: int | None = None,
    resource_scales: dict[str, Any] | None = None,
) -> list[Any]:
    """Build a parallel task graph for jobmon.

    Parameters
    ----------
    jobmon_tool
        The jobmon tool.
    runner
        The runner to use for the task.
    task_name
        The name of the task.
    node_args
        The arguments to the task script that are unique to each task. The keys of
        the dict are the names of the arguments and the values are lists of the
        values to use for each task. A dict with multiple keys will result in a
        cartesian product of the values. Mutually exclusive with
        flat_node_args.
    flat_node_args
        The arguments to the task script that are unique to each task. The first
        element of the tuple is the names of the arguments and the second element
        is a list of tuples of the values to use for each task. This can be used
        to avoid the cartesian product of node_args and just run a subset of the
        possible tasks. Mutually exclusive with node_args.
    task_args
        The arguments to the task script that are the same for each task, but
        alter the behavior of the task (e.g. input and output root directories).
    op_args
        Arguments that are passed to the task script but do not alter the logical
        behavior of the task (e.g. number of cores, logging verbosity).
    task_resources
        The resources to allocate to the task.
    max_attempts
        The maximum number of attempts to make for each task.
    resource_scales
        How much users want to scale their resource request if the
        the initial request fails. Scale factor can be a numeric value, a Callable
        that will be applied to the existing resources, or an Iterator. Any Callable
        should take a single numeric value as its sole argument. Any Iterator should
        only yield numeric values. Any Iterable can be easily converted to an
        Iterator by using the iter() built-in (e.g. iter([80, 160, 190])).


    Returns
    -------
    list
        A list of tasks to run.
    """
    for arg in ["stdout", "stderr"]:
        task_resources[arg] = str(task_resources.get(arg, "/tmp"))  # noqa: S108

    if node_args is not None and flat_node_args is not None:
        msg = "node_args and flat_node_args are mutually exclusive."
        raise ValueError(msg)
    if flat_node_args is not None:
        node_arg_string = " ".join(
            f"--{arg} {{{arg.replace('-', '_')}}}" for arg in flat_node_args[0]
        )
        flat_node_args = (
            tuple([arg.replace("-", "_") for arg in flat_node_args[0]]),
            flat_node_args[1],
        )
        clean_node_args: dict[str, Collection[Any]] = {k: [] for k in flat_node_args[0]}
    else:
        clean_node_args, node_arg_string = _process_args(node_args)
    clean_task_args, task_arg_string = _process_args(task_args)
    clean_op_args, op_arg_string = _process_args(op_args)

    command_template = (
        f"{runner} {task_name} {node_arg_string} {task_arg_string} {op_arg_string}"
    )

    task_template = jobmon_tool.get_task_template(
        default_compute_resources=task_resources,
        template_name=f"{task_name}_task_template",
        default_cluster_name="slurm",
        command_template=command_template,
        node_args=list(clean_node_args),
        task_args=list(clean_task_args),
        op_args=list(clean_op_args),
    )

    if flat_node_args is not None:
        tasks = []
        arg_names, arg_values = flat_node_args
        for args in arg_values:
            task_args = {
                **dict(zip(arg_names, args, strict=False)),
                **clean_task_args,
                **clean_op_args,
            }
            task = task_template.create_task(
                **task_args,
                max_attempts=max_attempts,
                resource_scales=resource_scales,
            )
            tasks.append(task)
    else:
        tasks = task_template.create_tasks(
            **clean_node_args,
            **clean_task_args,
            **clean_op_args,
            max_attempts=max_attempts,
            resource_scales=resource_scales,
        )
    return tasks


def run_workflow(  # type: ignore[no-untyped-def]
    workflow,
    log_method: Callable[[str], None] = print,
    **workflow_kwargs,
) -> str:
    # Calling workflow.bind() first just so that we can get the workflow id
    workflow.bind()
    log_method("Workflow creation complete.")
    log_method(f"Running workflow with ID {workflow.workflow_id}.")
    log_method("For full information see the Jobmon GUI:")
    log_method(
        f"https://jobmon-gui.ihme.washington.edu/#/workflow/{workflow.workflow_id}"
    )

    if "seconds_until_timeout" not in workflow_kwargs:
        # Jobmon defaults to 10 hours, but this is too short for us in general
        workflow_kwargs["seconds_until_timeout"] = 60 * 60 * 24 * 3

    # run workflow
    status = workflow.run(**workflow_kwargs)
    log_method(f"Workflow {workflow.workflow_id} completed with status {status}.")
    return str(status)


def make_log_dir(
    output_dir: str | Path,
) -> Path:
    run_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")  # noqa: DTZ005
    if "logs" in str(output_dir):
        log_dir = Path(output_dir) / run_time
    else:
        log_dir = Path(output_dir) / "zzz_logs" / run_time
    mkdir(log_dir, parents=True)
    mkdir(log_dir / "output")
    mkdir(log_dir / "error")
    return log_dir


def run_parallel(  # noqa: PLR0913
    runner: str,
    task_name: str,
    task_resources: dict[str, str | int],
    *,
    node_args: dict[str, Collection[Any] | None] | None = None,
    flat_node_args: tuple[tuple[str, ...], Collection[tuple[Any, ...]]] | None = None,
    task_args: dict[str, Any] | None = None,
    op_args: dict[str, Any] | None = None,
    concurrency_limit: int = 10000,
    max_attempts: int | None = None,
    resource_scales: dict[str, Any] | None = None,
    log_root: str | Path | None = None,
    log_method: Callable[[str], None] = print,
) -> str:
    """Run a parallel set of tasks using Jobmon.

    This helper function encapsulates one of the simpler workflow patterns in Jobmon:
    a set of tasks that run in parallel, each with the same command but
    different arguments. More complicated workflows should be implemented
    directly.

    Parameters
    ----------
    runner
        The runner to use for the task. Default is 'rptask'.
    task_name
        The name of the task to run.  Will also be used as the tool and workflow name.
    task_resources
        The resources to allocate to the task.
    node_args
        The arguments to the task script that are unique to each task. The keys of
        the dict are the names of the arguments and the values are lists of the
        values to use for each task. A dict with multiple keys will result in a
        cartesian product of the values. Mutually exclusive with
        flat_node_args.
    flat_node_args
        The arguments to the task script that are unique to each task. The first
        element of the tuple is the names of the arguments and the second element
        is a list of tuples of the values to use for each task. This can be used
        to avoid the cartesian product of node_args and just run a subset of the
        possible tasks. Mutually exclusive with node_args.
    task_args
        The arguments to the task script that are the same for each task, but
        alter the behavior of the task (e.g. input and output root directories).
    op_args
        Arguments that are passed to the task script but do not alter the logical
        behavior of the task (e.g. number of cores, logging verbosity).
    concurrency_limit
        The maximum number of tasks to run concurrently. Default is 10000.
    max_attempts
        The maximum number of attempts to make for each task.
    resource_scales
        How much users want to scale their resource request if the
        the initial request fails. Scale factor can be a numeric value, a Callable
        that will be applied to the existing resources, or an Iterator. Any Callable
        should take a single numeric value as its sole argument. Any Iterator should
        only yield numeric values. Any Iterable can be easily converted to an
        Iterator by using the iter() built-in (e.g. iter([80, 160, 190])).
    log_root
        The root directory for the logs. Default is None.
    log_method
        The method to use for logging. Default is print.

    Returns
    -------
    str
        The status of the workflow.
    """
    if node_args is not None and flat_node_args is not None:
        msg = "node_args and flat_node_args are mutually exclusive."
        raise ValueError(msg)

    if log_root is None:
        if task_args is None or "output-dir" not in task_args:
            msg = (
                "The task_args dictionary must contain an 'output-dir' key if no "
                "log_root is provided."
            )
            raise KeyError(msg)
        log_root = Path(task_args["output-dir"])
    log_dir = make_log_dir(log_root)
    task_resources["stdout"] = str(log_dir / "output")
    task_resources["standard_output"] = str(log_dir / "output")
    task_resources["stderr"] = str(log_dir / "error")
    task_resources["standard_error"] = str(log_dir / "error")

    tool = get_jobmon_tool(workflow_name=task_name)
    workflow = tool.create_workflow(
        name=f"{task_name}_{uuid.uuid4()}",
        max_concurrently_running=concurrency_limit,
    )

    tasks = build_parallel_task_graph(
        jobmon_tool=tool,
        task_name=task_name,
        node_args=node_args,
        flat_node_args=flat_node_args,
        task_args=task_args,
        op_args=op_args,
        task_resources=task_resources,
        runner=runner,
        max_attempts=max_attempts,
        resource_scales=resource_scales,
    )

    workflow.add_tasks(tasks)
    return run_workflow(workflow, log_method)
