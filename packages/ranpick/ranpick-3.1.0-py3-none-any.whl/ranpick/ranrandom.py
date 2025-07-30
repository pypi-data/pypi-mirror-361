from typing import Union, Tuple, List
import random


class RanpickError(Exception):
    """Custom error for ranpick-related issues."""
    def __init__(self, message: str, code: str = ""):
        super().__init__(f"{message}: {code}")
        self.code = code


def ranrandom(*options: Union[str, Tuple[str, int]], **kwargs) -> Union[str, List[str]]:
    """
    Select random items from a list, with optional duplicate selection.
    
    - Parameters:
        - `options`: Items to choose from, with optional probabilities.
        - `DS` (keyword argument): Number of duplicates to select (int).
        - `as_list` (keyword argument): If True, returns the result as a list (default: False).
    
    - Returns:
        - A single item (str) or a list of selected items based on `DS` and `as_list`.
    """
    # Handle keyword arguments
    ds_count = kwargs.get("DS", 1)  # Default: single selection
    as_list = kwargs.get("as_list", False)  # Default: return as comma-separated string

    if len(options) < 2:
        raise RanpickError("At least two options must be provided", code=str(options))

    if not isinstance(ds_count, int) or ds_count < 1:
        raise RanpickError(
            "Invalid DS value. It must be an integer greater than or equal to 1.",
            code=str(ds_count)
        )

    items = []
    probabilities = []
    fixed_probability_sum = 0  # Sum of explicitly specified probabilities
    unspecified_count = 0     # Count of items without specified probabilities

    # Parse input options and calculate probabilities
    for option in options:
        if isinstance(option, tuple):
            item, probability = option
            if not isinstance(probability, int) or probability < 0:
                raise RanpickError(
                    "Invalid probability value",
                    code=str(option)
                )
            items.append(item)
            probabilities.append(probability)
            fixed_probability_sum += probability
        elif isinstance(option, str):
            items.append(option)
            probabilities.append(None)  # Mark as unspecified probability
            unspecified_count += 1
        else:
            raise RanpickError(
                "Invalid option format",
                code=str(option)
            )

    # Handle unspecified probabilities
    if unspecified_count > 0:
        remaining_probability = 100 - fixed_probability_sum
        if remaining_probability < 0:
            raise RanpickError(
                "The sum of specified probabilities exceeds 100",
                code=str(options)
            )
        equal_share = remaining_probability // unspecified_count
        for i in range(len(probabilities)):
            if probabilities[i] is None:
                probabilities[i] = equal_share

        # Distribute any leftover probability
        remaining_mod = remaining_probability % unspecified_count
        for i in range(remaining_mod):
            probabilities[i] += 1

    # Verify total probability
    if sum(probabilities) != 100:
        raise RanpickError(
            "The sum of each probability does not add up to 100",
            code=str(options)
        )

    # Perform random selections
    if ds_count == 1:
        selected = random.choices(items, weights=probabilities, k=1)[0]
    else:
        selected = random.choices(items, weights=probabilities, k=ds_count)

    # Return as a list or a comma-separated string
    if as_list:
        return selected  # Keep as list
    else:
        if ds_count == 1:
            return str(selected)  # Single selection as a string
        return ",".join(selected)  # Properly join list items for multiple selections
