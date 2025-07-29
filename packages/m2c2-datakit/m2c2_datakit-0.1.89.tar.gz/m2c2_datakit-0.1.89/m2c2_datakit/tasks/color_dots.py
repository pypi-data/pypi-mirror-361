import ast
import json

import numpy as np
import pandas as pd

from ..core import helpers

""" 
TODO: Scoring and Summarizing Variables
* NOTE: The "incorrect" variables are a combination of "swap" and "random" responses. "Swap" variables are only for the "swap" responses.
? QUESTION: Should I change the "incorrect" variables to be "random" only?
"""


def _deserialize_if_needed(cells, cell_data_type="list"):
    """
    Ensure cell data is a list of dictionaries or a dictionary.

    Args:
        cells (str, list, or dict): The cell data to deserialize.
        cell_data_type (str): The expected type of the cell data. One of ["list","dict"]. Defaults to "list".

    Returns:
        Out: "list" or "dict". The deserialized cell data.
    """
    if cell_data_type == "list":
        if isinstance(cells, str):
            try:
                # Try JSON first
                cells = json.loads(cells)
            except json.JSONDecodeError:
                try:
                    # Fallback to Python literal eval
                    cells = ast.literal_eval(cells)
                except (ValueError, SyntaxError):
                    return []  # Return empty list on failure

        return cells if isinstance(cells, list) else []

    elif cell_data_type == "dict":
        if isinstance(cells, str):
            try:
                # Try JSON first
                cells = json.loads(cells)
            except json.JSONDecodeError:
                try:
                    # Fallback to Python literal eval
                    cells = ast.literal_eval(cells)
                except (ValueError, SyntaxError):
                    return {}  # Return empty dict on failure

        return cells if isinstance(cells, dict) else {}

    else:
        raise ValueError(f"Unknown cell_data_type '{cell_data_type}'")


def score_dots(row, method="location", location_delta=75):
    """
    General-purpose scoring function for color dots task.
    Location and color accuracy swap categorization.

    Args:
        row (pd.Series): A single trial's data.
        method (str): One of ["location", "color"].
        location_delta (int): Threshold for location accuracy. Defaults to 75.

    Returns:
        str: "Correct", "Swap", or "Random" based on the scoring criteria.
    """

    try:
        presented_dots = _deserialize_if_needed(
            row["presented_dots"], cell_data_type="list"
        )

        if method == "location":
            location_selected = _deserialize_if_needed(
                row["location_selected"], cell_data_type="dict"
            )
            location_selected = np.array(
                [location_selected["x"], location_selected["y"]]
            )

            if row["location_selected_delta"] <= location_delta:
                return "Correct"
            elif any(
                np.linalg.norm(
                    np.array([dot["location"]["x"], dot["location"]["y"]])
                    - location_selected
                )
                <= location_delta
                for dot in presented_dots
            ):
                return "Swap"
            else:
                return "Random"

        elif method == "color":
            color_selected = _deserialize_if_needed(
                row["color_selected"], cell_data_type="dict"
            )
            color_presented = {
                "color_name": presented_dots[row["color_target_dot_index"]][
                    "color_name"
                ],
                "rgba_color": presented_dots[row["color_target_dot_index"]][
                    "rgba_color"
                ],
            }

            if color_selected == color_presented:
                return "Correct"
            elif any(
                dot["color_name"] == color_selected["color_name"]
                for dot in presented_dots
            ):
                return "Swap"
            else:
                return "Random"

        else:
            raise ValueError(f"Unknown method '{method}'")

    except Exception as e:
        print(f"Error processing row: {e}")
        return None


# Wrapper-Compatible Functions
def score_accuracy_location(row):
    return score_dots(row, method="location", location_delta=75)


def score_acccuracy_color(row):
    return score_dots(row, method="color")


def summarize(x, trials_expected=20, rt_outlier_low=100, rt_outlier_high=10000):
    """
    Summarizes color dots task performance.

    Args:
        x (pd.DataFrame): Trial-level scored dataset.
        trials_expected (int): Number of trials expected. Defaults to 20.
        rt_outlier_low (int): Threshold for Low RT Outliers in milliseconds. Defaults to 100.
        rt_outlier_high (int): Threshold for High RT Outliers in milliseconds. Defaults to 10000.

    Returns:
        pd.Series: Summary statistics.
    """

    # ABSTRACTION TO APPEAR IN EACH SCORING SCRIPT
    d = helpers.summarize_common_metadata(x, trials_expected)

    # Tabulate Accuracy
    # Swaps Only
    d["n_trials_color_swap"] = sum(x["metric_accuracy_color"] == "Swap")
    d["n_trials_location_swap"] = sum(x["metric_accuracy_location"] == "Swap")
    d["n_responses_swap_total"] = d["n_trials_color_swap"] + d["n_trials_location_swap"]
    # All Incorrect (Swaps + Random)
    d["n_trials_color_incorrect"] = sum(x["metric_accuracy_color"] != "Correct")
    d["n_trials_location_incorrect"] = sum(x["metric_accuracy_location"] != "Correct")
    d["n_responses_incorrect_total"] = (
        d["n_trials_color_incorrect"] + d["n_trials_location_incorrect"]
    )
    # Correct
    d["n_trials_color_correct"] = sum(x["metric_accuracy_color"] == "Correct")
    d["n_trials_location_correct"] = sum(x["metric_accuracy_location"] == "Correct")
    d["n_responses_correct_total"] = (
        d["n_trials_color_correct"] + d["n_trials_location_correct"]
    )

    # Filter out outliers: RT < 100 ms or RT > 10,000 ms
    rt_filtered_color = x.loc[
        (x["color_selection_response_time_ms"] >= rt_outlier_low)
        & (x["color_selection_response_time_ms"] <= rt_outlier_high),
        "color_selection_response_time_ms",
    ]
    d["median_response_time_color_filtered"] = rt_filtered_color.median()

    rt_filtered_location = x.loc[
        (x["location_selection_response_time_ms"] >= rt_outlier_low)
        & (x["location_selection_response_time_ms"] <= rt_outlier_high),
        "location_selection_response_time_ms",
    ]
    d["median_response_time_location_filtered"] = rt_filtered_location.median()

    # RT for Correct AND RT within bounds
    rt_filtered_and_correct_color = x.loc[
        (x["metric_accuracy_color"] == "Correct")
        & (x["color_selection_response_time_ms"] >= rt_outlier_low)
        & (x["color_selection_response_time_ms"] <= rt_outlier_high),
        "color_selection_response_time_ms",
    ]
    d["median_response_time_color_filtered_correct"] = (
        rt_filtered_and_correct_color.median()
    )

    rt_filtered_and_correct_location = x.loc[
        (x["metric_accuracy_location"] == "Correct")
        & (x["location_selection_response_time_ms"] >= rt_outlier_low)
        & (x["location_selection_response_time_ms"] <= rt_outlier_high),
        "location_selection_response_time_ms",
    ]
    d["median_response_time_location_filtered_correct"] = (
        rt_filtered_and_correct_location.median()
    )

    # RT for Swaps AND RT within bounds
    rt_filtered_and_swap_color = x.loc[
        (x["metric_accuracy_color"] == "Swap")
        & (x["color_selection_response_time_ms"] >= rt_outlier_low)
        & (x["color_selection_response_time_ms"] <= rt_outlier_high),
        "color_selection_response_time_ms",
    ]
    d["median_response_time_color_filtered_swap"] = rt_filtered_and_swap_color.median()

    rt_filtered_and_swap_location = x.loc[
        (x["metric_accuracy_location"] == "Swap")
        & (x["location_selection_response_time_ms"] >= rt_outlier_low)
        & (x["location_selection_response_time_ms"] <= rt_outlier_high),
        "location_selection_response_time_ms",
    ]
    d["median_response_time_location_filtered_swap"] = (
        rt_filtered_and_swap_location.median()
    )

    # RT for Incorrect (swap & random) AND RT within bounds
    rt_filtered_and_incorrect_color = x.loc[
        (x["metric_accuracy_color"] != "Correct")
        & (x["color_selection_response_time_ms"] >= rt_outlier_low)
        & (x["color_selection_response_time_ms"] <= rt_outlier_high),
        "color_selection_response_time_ms",
    ]
    d["median_response_time_color_filtered_incorrect"] = (
        rt_filtered_and_incorrect_color.median()
    )

    rt_filtered_and_incorrect_location = x.loc[
        (x["metric_accuracy_location"] != "Correct")
        & (x["location_selection_response_time_ms"] >= rt_outlier_low)
        & (x["location_selection_response_time_ms"] <= rt_outlier_high),
        "location_selection_response_time_ms",
    ]
    d["median_response_time_location_filtered_incorrect"] = (
        rt_filtered_and_incorrect_location.median()
    )

    # return as series
    return pd.Series(d)
