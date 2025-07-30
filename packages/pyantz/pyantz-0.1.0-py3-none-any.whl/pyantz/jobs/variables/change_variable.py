"""Change variable will change the value of one variable and submit the next pipeline
in its config.

**NOTE: variables cannot be changed in a parent context; so this submits a NEW pipeline**

The main purpose is either to rename a variable or to change a configuration
    between steps or keep a counter

Because variables support basic math, it is possible to keep a counter with this
    var = %{var + 1} will count the variable up

For example, a user could set up two models where the first takes arg 'a' and
    the second takes arg 'b' and run them with the same variable
"""

import logging
from collections.abc import Mapping

from pydantic import BaseModel

import pyantz.infrastructure.config.base as config_base
from pyantz.infrastructure.core.status import Status


class Parameters(BaseModel, frozen=True):
    """See change variable docs"""

    left_hand_side: str
    right_hand_side: config_base.PrimitiveType


@config_base.mutable_job(Parameters)
def change_variable(
    parameters: config_base.ParametersType,
    variables: Mapping[str, config_base.PrimitiveType],
    logger: logging.Logger,
    *_,
    **__,
) -> tuple[Status, Mapping[str, config_base.PrimitiveType]]:
    """Change a variable to a new value

    Parameters {
        left_hand_side (str): name of the variable to change (left of equal sign)
        right_hand_side (str | int | bool | float): value to set the variable to
    }

    Args:
        parameters (ParametersType): _description_
        submit_fn (SubmitFunctionType): function to submit the pipeline to for execution
        variables (Mapping[str, PrimitiveType]): variables from the outer context
        logger (logging.Logger): logger to assist with debugging


    Returns:
        Status: SUCCESS if jobs successfully submitted; ERROR otherwise
    """

    params_parsed = Parameters.model_validate(parameters)

    logger.debug(
        "Changing variable %s to %s",
        params_parsed.left_hand_side,
        params_parsed.right_hand_side,
    )

    new_vars = {
        **variables,
        params_parsed.left_hand_side: params_parsed.right_hand_side,
    }

    return Status.SUCCESS, new_vars
