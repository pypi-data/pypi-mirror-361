"""Utilities for configurations."""

import ast
import os


def get_bool_env(env_var_name: str, default: str = "False") -> bool:
    """Convert a 'string boolean' env variable into a true boolean.

    Args:
        env_var_name: Name of target environment variable.
        default: Default if said environment variable isn't defined.

    Returns:
        The env variable as a boolean.

    Raises:
        ValueError: If the env variable isn't a 'string boolean'.
    """
    env_var: str = os.getenv(env_var_name, default)
    try:
        env_var = ast.literal_eval(env_var.title())
        if isinstance(env_var, bool):
            return env_var
        raise ValueError
    except (
        SyntaxError,
        ValueError,
    ) as err:
        raise ValueError(f"Invalid boolean value: {env_var}") from err
