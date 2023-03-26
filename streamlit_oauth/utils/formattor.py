from typing import Union, Optional

like_number = Union[float, int, str]
number = Union[float, int]


def str_to_number(number: str) -> float:
    try:
        float_number = float(number)
        return float_number
    except:
        raise ValueError(f"Failed to implicitly convert {number} to a float or an int.")


def number_format(number: like_number, dp: Optional[int] = 0) -> str:

    if isinstance(number, str):
        number = str_to_number(number)

    return f"{round(number, dp):,}"
