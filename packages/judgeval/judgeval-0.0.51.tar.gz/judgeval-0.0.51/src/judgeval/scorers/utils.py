"""
Util functions for Scorer objects
"""

import asyncio
import nest_asyncio
import inspect
import json
import sys
import re
from contextlib import contextmanager
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.console import Console
from typing import List, Optional

from judgeval.scorers import JudgevalScorer
from judgeval.data import Example, ExampleParams
from judgeval.scorers.exceptions import MissingExampleParamsError


def clone_scorers(scorers: List[JudgevalScorer]) -> List[JudgevalScorer]:
    """
    Creates duplicates of the scorers passed as argument.
    """
    cloned_scorers = []
    for s in scorers:
        scorer_class = type(s)
        args = vars(s)

        signature = inspect.signature(scorer_class.__init__)
        valid_params = signature.parameters.keys()
        valid_args = {key: args[key] for key in valid_params if key in args}

        cloned_scorer = scorer_class(**valid_args)
        # kinda hacky, but in case the class inheriting from JudgevalScorer doesn't have `model` in its __init__,
        # we need to explicitly include it here so that we can add the judge model to the cloned scorer
        cloned_scorer._add_model(model=args.get("model"))
        cloned_scorers.append(cloned_scorer)
    return cloned_scorers


def scorer_console_msg(
    scorer: JudgevalScorer,
    async_mode: Optional[bool] = None,
):
    """
    Renders a message to be displayed to console when a scorer is being executed.
    """
    if async_mode is None:
        run_async = scorer.async_mode
    else:
        run_async = async_mode

    return f"🔨 Executing Judgment's [rgb(106,0,255)]{scorer.__name__} Scorer[/rgb(106,0,255)]! \
        [rgb(55,65,81)](using {scorer.evaluation_model}, async_mode={run_async})...[/rgb(55,65,81)]"


@contextmanager
def scorer_progress_meter(
    scorer: JudgevalScorer,
    async_mode: Optional[bool] = None,
    display_meter: bool = True,
    total: int = 100,
    transient: bool = True,
):
    """
    Context manager to display a progress indicator (spinner) while a scorer is being run.
    """
    console = Console(file=sys.stderr)
    if display_meter:
        with Progress(
            SpinnerColumn(style="rgb(106,0,255)"),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=transient,
        ) as progress:
            progress.add_task(
                description=scorer_console_msg(scorer, async_mode),
                total=total,
            )
            yield
    else:
        yield


def parse_response_json(
    llm_response: str, scorer: Optional[JudgevalScorer] = None
) -> dict:
    """
    Extracts JSON output from an LLM response and returns it as a dictionary.

    If the JSON is invalid, the error is forwarded to the `scorer`, if provided.

    Args:
        llm_response (str): The response from an LLM.
        scorer (JudgevalScorer, optional): The scorer object to forward errors to (if any).
    """
    start = llm_response.find("{")  # opening bracket
    end = llm_response.rfind("}") + 1  # closing bracket

    if end == 0 and start != -1:  # add the closing bracket if it's missing
        llm_response = llm_response + "}"
        end = len(llm_response)

    json_str = (
        llm_response[start:end] if start != -1 and end != 0 else ""
    )  # extract the JSON string
    json_str = re.sub(
        r",\s*([\]}])", r"\1", json_str
    )  # Remove trailing comma if present

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        error_str = "Evaluation LLM outputted an invalid JSON. Please use a stronger evaluation model."
        if scorer is not None:
            scorer.error = error_str
        raise ValueError(error_str)
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")


def print_verbose_logs(metric: str, logs: str):
    print("*" * 50)
    print(f"{metric} Verbose Logs")
    print("*" * 50)
    print("")
    print(logs)
    print("")
    print("=" * 70)


def create_verbose_logs(metric: JudgevalScorer, steps: List[str]) -> str:
    """
    Creates verbose logs for a scorer object.

    Args:
        metric (JudgevalScorer): The scorer object.
        steps (List[str]): The steps to be included in the verbose logs.

    Returns:
        str: The verbose logs (Concatenated steps).
    """

    verbose_logs = ""
    for i in range(len(steps) - 1):
        verbose_logs += steps[i]
        if i < len(steps) - 2:  # don't add new line for penultimate step
            verbose_logs += " \n \n"
    if metric.verbose_mode:
        print_verbose_logs(metric.__name__, verbose_logs + f"\n \n{steps[-1]}")
    return verbose_logs


def get_or_create_event_loop() -> asyncio.AbstractEventLoop:
    """
    Get or create an asyncio event loop.

    This function attempts to retrieve the current event loop using `asyncio.get_event_loop()`.
    If the event loop is already running, it applies the `nest_asyncio` patch to allow nested
    asynchronous execution. If the event loop is closed or not found, it creates a new event loop
    and sets it as the current event loop.

    Returns:
        asyncio.AbstractEventLoop: The current or newly created event loop.

    Raises:
        RuntimeError: If the event loop is closed.
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            print(
                "Event loop is already running. Applying nest_asyncio patch to allow async execution..."
            )
            nest_asyncio.apply()

        if loop.is_closed():
            raise RuntimeError
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


def check_example_params(
    example: Example,
    example_params: List[ExampleParams],
    scorer: JudgevalScorer,
):
    if isinstance(example, Example) is False:
        error_str = f"in check_example_params(): Expected example to be of type 'Example', but got {type(example)}"
        scorer.error = error_str
        raise MissingExampleParamsError(error_str)

    missing_params = []
    for param in example_params:
        if getattr(example, param.value) is None:
            missing_params.append(f"'{param.value}'")

    if missing_params:
        if len(missing_params) == 1:
            missing_params_str = missing_params[0]
        elif len(missing_params) == 2:
            missing_params_str = " and ".join(missing_params)
        else:
            missing_params_str = (
                ", ".join(missing_params[:-1]) + ", and " + missing_params[-1]
            )

        error_str = f"{missing_params_str} fields in example cannot be None for the '{scorer.__name__}' scorer"
        scorer.error = error_str
        raise MissingExampleParamsError(error_str)
