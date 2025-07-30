"""If then conditionally submits a pipeline based on a conditional

By default, ANTZ supports conditions based on primitive types (lt, gt, ge, le, ne, eq)
    but a user can specify their own comparator function to create a much more powerful operator
"""

# pylint: disable=duplicate-code

import logging
import operator
from collections.abc import Mapping
from typing import Any, Callable, Literal

from pydantic import BaseModel

import pyantz.infrastructure.config.base as config_base
from pyantz.infrastructure.core.status import Status


class Parameters(BaseModel, frozen=True):
    """See compare function docstring"""

    comparator: Literal["<", ">", "<=", ">=", "==", "!="]
    left: config_base.PrimitiveType
    right: config_base.PrimitiveType
    if_true: config_base.PipelineConfig
    if_false: config_base.PipelineConfig


comparators: dict[str, Callable[[Any, Any], bool]] = {
    "==": operator.eq,
    "!=": operator.ne,
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
}


@config_base.submitter_job(Parameters)
def compare(
    parameters: config_base.ParametersType,
    submit_fn: config_base.SubmitFunctionType,
    variables: Mapping[str, config_base.PrimitiveType],
    _pipeline_config: config_base.PipelineConfig,
    logger: logging.Logger,
) -> Status:
    """Split the execution based on a comparison between two values (left/right)

    Useful when paired with the "update variable"

    ParamterersType {
        "comparator" (Literal): can be
            "<": left hand and right hand field required.
                True if left is less than right
            "<=": left hand and right hand field required.
                True if left is less than or equal to right
            ">": left hand and right hand field required.
                True if left is greater than right
            ">=": left hand and right hand field required.
                True if left is greater than or equal to right
            "!=": left hand and right hand field required.
                True if left is not equal to right
            "==": left hand and right hand field required.
                True if left is equal to right
        "left" (str | int | bool | float): left value for comparator expression
        "right" (str | int | bool | float): right value for comparator expression
        "if_true" (PipelineConfig): if the comparator expression is true, evaluate this pipeline
        "if_false" (PipelineConfig): if the comparator expression is false, evaluate this pipeline
    }

    Args:
        parameters (ParametersType): See doc string above
        submit_fn (SubmitFunctionType): function to submit the pipeline to for execution
        variables (Mapping[str, PrimitiveType]): variables from the outer context
        logger (logging.Logger): logger to assist with debugging

    Returns:
        Status: SUCCESS if the job didn't error; else ERROR
    """

    parameters_parsed = Parameters.model_validate(parameters)
    logger.debug("Parameters successfully parsed")

    result = comparators[parameters_parsed.comparator](
        parameters_parsed.left, parameters_parsed.right
    )
    logger.debug("Comparator returned %s", result)

    if result:
        submit_fn(
            config_base.Config.model_validate(
                {"variables": variables, "config": parameters_parsed.if_true}
            )
        )
    else:
        submit_fn(
            config_base.Config.model_validate(
                {"variables": variables, "config": parameters_parsed.if_false}
            )
        )

    return Status.FINAL
