import logging
import time
from collections import defaultdict
from pathlib import Path

import click
import pandas as pd
from loguru import logger

from rra_tools.logging.protocol import SupportsLogging


class TaskPerformanceLogger(SupportsLogging):
    def __init__(self) -> None:
        self.current_context = ""
        self.current_context_start = 0.0
        self.times: dict[str, float] = defaultdict(float)

    def _record_timing(self, context: str | None) -> None:
        if context is None:
            return

        if not self.current_context:
            self.current_context = context
            self.current_context_start = time.time()
        else:
            self.times[self.current_context] += time.time() - self.current_context_start
            self.current_context = context
            self.current_context_start = time.time()

    def log(
        self,
        level: int,
        message: str,
        *args: str,
        context: str | None = None,
        **kwargs: str,
    ) -> None:
        if context is not None:
            self._record_timing(context)
        logger.log(level, message, *args, **kwargs)

    def info(
        self,
        message: str,
        *args: str,
        context: str | None = None,
        **kwargs: str,
    ) -> None:
        self.log(logging.INFO, message, *args, context=context, **kwargs)

    def debug(
        self,
        message: str,
        *args: str,
        context: str | None = None,
        **kwargs: str,
    ) -> None:
        self.log(logging.DEBUG, message, *args, context=context, **kwargs)

    def warning(
        self,
        message: str,
        *args: str,
        context: str | None = None,
        **kwargs: str,
    ) -> None:
        self.log(logging.WARNING, message, *args, context=context, **kwargs)

    def error(
        self,
        message: str,
        *args: str,
        context: str | None = None,
        **kwargs: str,
    ) -> None:
        self.log(logging.ERROR, message, *args, context=context, **kwargs)

    def exception(
        self,
        message: str,
        *args: str,
        context: str | None = None,
        **kwargs: str,
    ) -> None:
        self.log(logging.ERROR, message, *args, context=context, **kwargs)

    def critical(
        self,
        message: str,
        *args: str,
        context: str | None = None,
        **kwargs: str,
    ) -> None:
        self.log(logging.CRITICAL, message, *args, context=context, **kwargs)

    def report(self) -> None:
        if self.current_context is not None:
            self.times[self.current_context] += time.time() - self.current_context_start
        times = self.times.copy()
        times["total"] = sum(self.times.values())
        logger.info(
            "\nRuntime report\n"
            + "=" * 31
            + "\n"
            + "\n".join(
                [
                    f"{context:<20}:{elapsed_time:>10.2f}"
                    for context, elapsed_time in times.items()
                ]
            )
        )


task_performance_logger = TaskPerformanceLogger()


@click.command()
@click.argument(
    "log_dir", type=click.Path(exists=True, file_okay=False, resolve_path=True)
)
@click.argument("job_name", type=click.STRING)
def parse_logs(log_dir: str, job_name: str) -> None:
    result = defaultdict(list)
    log_paths = list(Path(log_dir).glob(f"{job_name}*"))
    if not log_paths:
        click.echo(f"No logs found for job name {job_name}. Exiting.")
        return

    for log_path in log_paths:
        with log_path.open() as f:
            log_data = f.readlines()
        for line in log_data[log_data.index("Runtime report\n") + 2 :]:
            metric, t = line.split(":")
            t, *_ = t.split("\x1b")
            result[metric.strip()].append(float(t.strip()))
    df = pd.DataFrame(result)
    summary = df.describe().T
    total = df.sum()
    summary["total"] = total
    click.echo(summary[["mean", "min", "max", "total"]])
