# RRA Tools

[![PyPI](https://img.shields.io/pypi/v/rra-tools?style=flat-square)](https://pypi.python.org/pypi/rra-tools/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rra-tools?style=flat-square)](https://pypi.python.org/pypi/rra-tools/)
[![PyPI - License](https://img.shields.io/pypi/l/rra-tools?style=flat-square)](https://pypi.python.org/pypi/rra-tools/)

---

**Documentation**: [https://ihmeuw.github.io/rra-tools](https://ihmeuw.github.io/rra-tools)

**Source Code**: [https://github.com/ihmeuw/rra-tools](https://github.com/ihmeuw/rra-tools)

**PyPI**: [https://pypi.org/project/rra-tools/](https://pypi.org/project/rra-tools/)

---

Common utilities for IHME Rapid Response team pipelines.

### CLI Tools

The provided cli tools break down into three categories.

#### Exception handling

The `cli_tools` subpackage provides a `handle_exceptions` wrapper that can be used to
wrap functions that may raise exceptions and drop into a pdb shell when an exception is
raised. This is useful for debugging functions that are failing in a pipeline.

```python
from rra_tools.cli_tools import handle_exceptions
from loguru import logger

def my_task():
    ...


if __name__ == "__main__":
    runner = handle_exceptions(my_task, logger, with_debugger=True)
    runner()
```

#### Dynamic module import

The `cli_tools` subpackage provides a `load_module_from_info` function that can be used
to dynamically import a module. This is a useful pattern for creating a CLI that can
dynamically add new commands and subcommands based on subpackage structure.

TODO: Usage example

#### Click options

The `cli_tools` subpackage provides several click options that can be used to create
CLI commands with common options.

- `with_verbose` - Add a `--verbose`, `-v` option to the command to increase the log
    verbosity
- `with_debugger` - Add a `--pdb` option to the command to drop into a pdb shell on
    exception
- `with_input_directory` - Add a parameterizeable `--{dir-name}-dir` option to the
    command to specify an input directory.
- `with_output_directory` - Add a `--output-dir`, `-o` option to the command to
    specify an output directory.
- `with_num_cores` - Add a `--num-cores`, `-c` option to the command to specify the
    number of cores to use for parallel processing.
- `with_queue` - Add a `--queue`, `-q` option to the command to specify a slurm queue
    to run jobs on.
- `with_progress_bar` - Add a `--progress-bar`, `--pb` option to the command to
    display a progress bar for long-running tasks.
- `with_dry_run` - Add a `--dry-run`, `-n` option to the command to run the command
    without actually executing the task.

These options do not provide implementations for the options, but rather provide a
standard interface for adding these options to a command to ensure consistency across
commands. Several of these options are meant to be used with other tools provided
in this package like exception handling, logging, and parallel processing.

```python
import click
from loguru import logger

from rra_tools.cli_tools import (
    with_verbose,
    with_debugger,
    with_output_directory,
    handle_exceptions,
)
from rra_tools.logging import configure_logging_to_terminal

def my_task_main(output_dir: str):
    ...


@click.command()
@with_output_directory("/path/to/default/output")
@with_verbose()
@with_debugger()
def my_task(output_dir: str, verbose: int, debugger: bool):
    configure_logging_to_terminal(verbose)
    runner = handle_exceptions(my_task_main, logger, with_debugger=debugger)
    runner(output_dir)

```

### Logging

The `logging` subpackage provides a number of utilities for configuring loggers
and for performance logging. This package is built on top of the `loguru` package,
which provides a more flexible and powerful logging interface than the standard
library `logging` package.

#### Configuration

There are three main functions for configuring loggers:

- `configure_logging_to_terminal` - Configure a logger to log to the terminal
- `configure_logging_to_file` - Configure a logger to log to a file
- `add_logging_sink` - A generic function to add a sink to a logger

The first two options are convenience functions that set up a logger with a standard
configuration. The third option is more flexible and can be used to add additional
sinks to a logger.

#### Performance Logging

The `logging` subpackage provides a `task_performance_logger` that is a drop-in
replacement for the `loguru` logger that logs the time taken to run a task.

```python
from rra_tools.logging import task_performance_logger as logger

def my_task():
    logger.debug("Loading training data", context="load_data")
    # Load the data

    logger.debug("Training model", context="train_model")
    # Train the model

    # Using the same context for logging will accumulate time
    # spent in that context across both usages.
    logger.debub("Loading inference_data", context="load_data")
    # Load the inference data

    logger.debug("Evaluating model", context="evaluate_model")
    # Evaluate the model

    logger.debug("Saving results", context="save_results")
    # Save the results

    logger.report()  # Prints out the time spent in each logging context

```

Additionally, `rra_tools` provides a command line tool `parse_logs` that can be used to
summarize the performance logs generated by the `task_performance_logger`. This is
useful when trying to understand the runtime characteristics of a pipeline that may
run hundreds or thousands of tasks.

```sh
parse_logs path/to/output/log/directory/
```

### Shell Tools

The `shell_tools` module provides a few functions to run common shell commands.

1. `wget` - Download a file from a URL

   ```python
    from rra_tools.shell_tools import wget

    wget("https://example.com/file.txt", "path/to/output.txt")
    ```

2. `unzip_and_delete_archive` - Unzip a file and delete the archive

   ```python
    from rra_tools.shell_tools import unzip_and_delete_archive

    unzip_and_delete_archive("path/to/archive.zip", "path/to/output")
    ```

    Note: you may need to install `unzip` on your system to use this function. You
    can do so with `conda install -c conda-forge unzip`.

3. `mkdir` - Create a directory with correct permissions.
    The default operation of mkdir via the `os` module or `pathlib` translates uses
    the umask of the user running the script along with the permissions set. This
    often results in unexpected permissions on the created directory. This function
    allows you to specify the permissions of the directory without relying on the
    umask.

    ```python
    from rra_tools.shell_tools import mkdir

    mkdir("path/to/directory", mode=0o755)
    # Can also make parents
    mkdir("path/to/other/directory", parents=True, mode=0o775)
    # Can also do a no-op if the directory already exists
    mkdir("path/to/other/directory", mode=0o775)
    ```

4. `touch` - Create a file with the correct permissions.
    Like `mkdir`, `touch` allows you to specify the permissions of the file without
    relying on the umask.

    ```python
    from rra_tools.shell_tools import touch

    touch("path/to/file.txt", mode=0o664)
    ```

### Parallel Processing with Multiprocessing

The `parallel` module provides a utility to run a function of a single argument in
parallel across a list of inputs using multiprocessing.

```python
from rra_tools.parallel import run_parallel

# Trivial example
def my_runner(x):
    return x ** 2

inputs = list(range(1000))

results = run_parallel(
    my_runner,
    inputs,
    num_cores=3,  # By default, num_cores is set to 1 and will run sequentially
)
```

In practice, the function we want to parallelize will be significantly more complex
than the trivial example above. Generally, you want to set things up so that:

1. The function you want to parallelize is self-contained and does not rely on any
    global state.
2. The function you want to parallelize is relatively expensive to run. If the
    function is cheap to run, the overhead of parallelization can outweigh the benefits
    of parallelization.
3. The input argument to the function is relatively small in memory. Multiprocessing
    needs to copy the input data to each worker process, so if the input data is large,
    the overhead of copying the data can outweigh the benefits of parallelization.
    A common way to overcome this limitation is to pass the path to the input data
    instead of the data itself and then have the function read the data from the path.
4. The function is not *too* complex. If your `runner` function is complicated, you may
    end up with resource contention between the worker processes that is hard to
    understand (e.g. you may run out of memory because each worker process is trying
    is loading a big dataset at the same time). There's no hard and fast rule here,
    but once functions get to be more than a few dozen lines long, you should start
    thinking about whether process-based parallelization is the right choice, and maybe
    opt for a different parallelization strategy (like `jobmon` described below).


### Jobmon Integration

The `jobmon` module provides a set of utilities to run more complicated parallel
jobs by interfacing with a job scheduler like `slurm`. See
[Jobmon documentation](https://jobmon.readthedocs.io/en/latest/index.html) for more
information.

#### Installation

Jobmon is not installed by default with `rra-tools` and is only available to download
and install on the IHME cluster. To install jobmon, you must have
a conf file in your home directory at `~/.pip/pip.conf` with the following contents:

```
[global]
extra-index-url = https://artifactory.ihme.washington.edu/artifactory/api/pypi/pypi-shared/simple
trusted-host = artifactory.ihme.washington.edu/artifactory/api/pypi/pypi-shared
```

Then you can install jobmon with:

```sh
pip install jobmon[ihme]
```

#### Usage

TBD


### Translation

The `translate` module provides functions to translate text files from one
language to another.


```python
from rra_tools.translate import translate_text_file

translate_text_file("path/to/input.txt", "path/to/output.txt")
```

By default, it will attempt to autodetect the language in the input file and produce
outputs in English, but you can specify the source and target languages:

```python
from rra_tools.translate import translate_text_file
# Translate from German to Spanish
translate_text_file(
    "path/to/input.txt",
    "path/to/output.txt",
    source_language="de",
    target_language="es",
)
```

The `translate` subpackage can also translate dataframe columns

```python
import pandas as pd
from rra_tools.translate import translate_dataframe

df = pd.DataFrame({"text": ["hola", "mundo"]})
translated_df = translate_dataframe(df, columns=["text"])
```


---

## Installation

```sh
pip install rra-tools
```

## Development

Instructions using conda:

1. Clone this repository.

    Over ssh:
    ```sh
    git clone git@github.com:ihmeuw/climate-downscale.git
    ```

    Over https:
    ```sh
    git clone https://github.com/ihmeuw/climate-downscale.git
    ```

2. Create a new conda environment.

    ```sh
    conda create -n climate-downscale python=3.10
    conda activate climate-downscale
    ```

3. Install `poetry` and the project dependencies.

    ```sh
    conda install poetry
    poetry install
    ```

### Documentation

The documentation is automatically generated from the content of the `docs` directory and from the docstrings
 of the public signatures of the source code. The documentation is updated and published as a [Github project page
 ](https://pages.github.com/) automatically as part each release.

### Releasing

Trigger the [Draft release workflow](https://github.com/collijk/rra-tools/actions/workflows/draft_release.yml)
(press _Run workflow_). This will update the changelog & version and create a GitHub release which is in _Draft_ state.

Find the draft release from the
[GitHub releases](https://github.com/collijk/rra-tools/releases) and publish it. When
 a release is published, it'll trigger [release](https://github.com/collijk/rra-tools/blob/master/.github/workflows/release.yml) workflow which creates PyPI
 release and deploys updated documentation.

### Pre-commit

Pre-commit hooks run all the auto-formatting (`ruff format`), linters (e.g. `ruff` and `mypy`), and other quality
 checks to make sure the changeset is in good shape before a commit/push happens.

You can install the hooks with (runs for each commit):

```sh
pre-commit install
```

Or if you want them to run only for each push:

```sh
pre-commit install -t pre-push
```

Or if you want e.g. want to run all checks manually for all files:

```sh
poetry run pre-commit run --all-files
```
