from typing import List, Optional, Union
from pydantic import BaseModel, field_validator, Field

from judgeval.data import Example, CustomExample
from judgeval.scorers import JudgevalScorer, APIJudgmentScorer
from judgeval.constants import ACCEPTABLE_MODELS


class EvaluationRun(BaseModel):
    """
    Stores example and evaluation scorers together for running an eval task

    Args:
        project_name (str): The name of the project the evaluation results belong to
        eval_name (str): A name for this evaluation run
        examples (Union[List[Example], List[CustomExample]]): The examples to evaluate
        scorers (List[Union[JudgmentScorer, JudgevalScorer]]): A list of scorers to use for evaluation
        model (str): The model used as a judge when using LLM as a Judge
        metadata (Optional[Dict[str, Any]]): Additional metadata to include for this evaluation run, e.g. comments, dataset name, purpose, etc.
        judgment_api_key (Optional[str]): The API key for running evaluations on the Judgment API
    """

    organization_id: Optional[str] = None
    project_name: Optional[str] = Field(default=None, validate_default=True)
    eval_name: Optional[str] = Field(default=None, validate_default=True)
    examples: Union[List[Example], List[CustomExample]]
    scorers: List[Union[APIJudgmentScorer, JudgevalScorer]]
    model: Optional[str] = "gpt-4.1"
    trace_span_id: Optional[str] = None
    # API Key will be "" until user calls client.run_eval(), then API Key will be set
    judgment_api_key: Optional[str] = ""
    override: Optional[bool] = False
    append: Optional[bool] = False

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)

        data["scorers"] = [
            scorer.to_dict()
            if hasattr(scorer, "to_dict")
            else scorer.model_dump()
            if hasattr(scorer, "model_dump")
            else {"score_type": scorer.score_type, "threshold": scorer.threshold}
            for scorer in self.scorers
        ]

        return data

    @field_validator("examples")
    def validate_examples(cls, v):
        if not v:
            raise ValueError("Examples cannot be empty.")

        first_type = type(v[0])
        if first_type not in (Example, CustomExample):
            raise ValueError(f"Invalid type for Example/CustomExample: {first_type}")
        if not all(isinstance(ex, first_type) for ex in v):
            raise ValueError(
                "All examples must be of the same type, either all Example or all CustomExample."
            )

        return v

    @field_validator("scorers")
    def validate_scorers(cls, v):
        if not v:
            raise ValueError("Scorers cannot be empty.")
        return v

    @field_validator("model")
    def validate_model(cls, v, values):
        if not v:
            raise ValueError("Model cannot be empty.")

        # Check if model is string or list of strings
        if isinstance(v, str):
            if v not in ACCEPTABLE_MODELS:
                raise ValueError(
                    f"Model name {v} not recognized. Please select a valid model name.)"
                )
            return v

    class Config:
        arbitrary_types_allowed = True
