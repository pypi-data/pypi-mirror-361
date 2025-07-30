from typing import List, Optional, Union
from judgeval.common.logger import debug
from pydantic import BaseModel
from judgeval.data import ScorerData, Example, CustomExample
from judgeval.data.trace import TraceSpan


class ScoringResult(BaseModel):
    """
    A ScoringResult contains the output of one or more scorers applied to a single example.
    Ie: One input, one actual_output, one expected_output, etc..., and 1+ scorer (Faithfulness, Hallucination, Summarization, etc...)

    Args:
        success (bool): Whether the evaluation was successful.
                        This means that all scorers applied to this example returned a success.
        scorer_data (List[ScorerData]): The scorers data for the evaluated example
        data_object (Optional[Example]): The original example object that was used to create the ScoringResult, can be Example, CustomExample (future), WorkflowRun (future)

    """

    # Fields for scoring outputs
    success: bool  # used for unit testing
    scorers_data: Union[List[ScorerData], None]
    name: Optional[str] = None

    # The original example object that was used to create the ScoringResult
    data_object: Optional[Union[TraceSpan, CustomExample, Example]] = None
    trace_id: Optional[str] = None

    # Additional fields for internal use
    run_duration: Optional[float] = None
    evaluation_cost: Optional[float] = None

    def to_dict(self) -> dict:
        """Convert the ScoringResult instance to a dictionary, properly serializing scorer_data."""
        return {
            "success": self.success,
            "scorers_data": [scorer_data.to_dict() for scorer_data in self.scorers_data]
            if self.scorers_data
            else None,
            "data_object": self.data_object.to_dict() if self.data_object else None,
        }

    def __str__(self) -> str:
        return f"ScoringResult(\
            success={self.success}, \
            scorer_data={self.scorers_data}, \
            data_object={self.data_object}, \
            run_duration={self.run_duration}, \
            evaluation_cost={self.evaluation_cost})"


def generate_scoring_result(
    data_object: Union[Example, TraceSpan],
    scorers_data: List[ScorerData],
    run_duration: float,
    success: bool,
) -> ScoringResult:
    """
    Creates a final ScoringResult object for an evaluation run based on the results from a completed LLMApiTestCase.

    When an LLMTestCase is executed, it turns into an LLMApiTestCase and the progress of the evaluation run is tracked.
    At the end of the evaluation run, we create a TestResult object out of the completed LLMApiTestCase.
    """
    if data_object.name is not None:
        name = data_object.name
    else:
        name = "Test Case Placeholder"
        debug(f"No name provided for example, using default name: {name}")
    debug(f"Creating ScoringResult for: {name}")
    scoring_result = ScoringResult(
        name=name,
        data_object=data_object,
        success=success,
        scorers_data=scorers_data,
        run_duration=run_duration,
        evaluation_cost=None,
    )
    return scoring_result
