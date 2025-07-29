"""Select items from the ABS Catalogue based on search criteria."""

import re
from collections.abc import Sequence
from enum import Enum
from typing import Unpack

import pandas as pd

from sdmxabs.download_cache import GetFileKwargs
from sdmxabs.fetch_multi import fetch_multi
from sdmxabs.flow_metadata import FlowMetaDict, code_lists, data_dimensions, data_flows


# --- some types specific to this module
class MatchType(Enum):
    """Enumeration for match types."""

    EXACT = 1
    PARTIAL = 2
    REGEX = 3


MatchItem = tuple[str, str, MatchType]  # pattern, dimension, MatchType
MatchCriteria = Sequence[MatchItem]  # Sequence of tuples containing (pattern, dimension, MatchType)


def package_codes(codes: list[str], dimension: str, return_dict: dict[str, str]) -> None:
    """Package the codes into the return dictionary for a given dimension.

    If the dimension already exists in the return_dict, we will intersect the newly
    identified  codes with the existing codes. If the intersection is a null set, the
    dimension will be removed from the return_dict (ie. the global match).

    Note: multiple matched codes are separated by a '+' sign in the return_dict.

    """
    if dimension in return_dict:
        previous = return_dict[dimension].split("+")
        codes = list(set(previous).intersection(set(codes)))
        if not codes:
            del return_dict[dimension]  # no matches, remove dimension
    if codes:
        return_dict[dimension] = "+".join(list(set(codes)))


# --- private functions
def get_codes(
    code_list_dict: FlowMetaDict,
    pattern: str,
    match_type: MatchType = MatchType.PARTIAL,
) -> list[str]:
    """Obtain all codes matching the pattern."""
    codes = []
    for code, code_list in code_list_dict.items():
        name = code_list.get("name", "")
        if not name:
            # should not happen.
            print(f"Code {code} has no name; (skipping)")
            continue
        match match_type:
            case MatchType.EXACT:
                if name == pattern:
                    codes.append(code)
            case MatchType.PARTIAL:
                # Case-insensitive partial match
                if pattern.lower() in name.lower():
                    codes.append(code)
            case MatchType.REGEX:
                if re.match(pattern, name):
                    codes.append(code)
    return codes


# --- public functions
def match_item(
    pattern: str,
    dimension: str,
    match_type: MatchType = MatchType.PARTIAL,
) -> MatchItem:
    """Create a new MatchItem for use in select_items() and fetch_selection().

    Args:
        pattern (str): The pattern to match.
        dimension (str): The dimension to match against.
        match_type (MatchType, optional): The type of match to perform. Defaults to MatchType.EXACT.

    Returns:
        MatchElement: A tuple representing the match element.

    """
    return (pattern, dimension, match_type)


def make_wanted(
    flow_id: str,
    criteria: MatchCriteria,
) -> pd.DataFrame:
    """Build the `wanted` Dataframe for use by fetch_multi() by matching flow metadata.

    Args:
        flow_id (str): The ID of the data flow to select items from.
        criteria (MatchElements): A sequence of tuples containing the element name,
            the value to match, and the match type (exact, partial, or regex).

    Returns:
        pd.DataFrame: A DataFrame containing the selected items, which can be dropped
            into the call of the function fetch_multi().

    Raises:
        ValueError: If the flow_id is not valid or if no items match the criteria.

    Notes:
    -   Should build a one line DataFrame. This Frame may select multiple data series,
        when passed to fetch_multi. It also can be concatenated with other DataFrames
        to build a larger selection.
    -   If two match elements refer to the same dimension, only the `intersection` of the
        matches will be returned.

    """
    # --- some sanity checks
    if flow_id not in data_flows():
        raise ValueError(f"Invalid flow_id: {flow_id}.")
    dimensions = data_dimensions(flow_id)
    if not dimensions:
        raise ValueError(f"No dimensions found for flow_id: {flow_id}.")

    # --- lets build the codelist dictionary
    return_dict: dict[str, str] = {}
    for pattern, dimension, match_type in criteria:
        if dimension not in dimensions:
            print(f"Dimension '{dimension}' not found for flow '{flow_id}'; (skipping)")
            continue
        dim_dict = dimensions[dimension]
        if "package" not in dim_dict or dim_dict["package"] != "codelist" or "id" not in dim_dict:
            print(f"Dimension '{dimension}' does not have a codelist; (skipping)")
            continue
        code_list_name = dim_dict.get("id")
        codes = get_codes(code_lists(code_list_name), pattern, match_type)
        package_codes(codes, dimension, return_dict)

    # --- return as a (one row) `wanted` DataFrame
    return_dict["flow_id"] = flow_id
    return pd.DataFrame([return_dict]).astype(str)


def fetch_selection(
    flow_id: str,
    criteria: MatchCriteria,
    *,
    validate: bool = False,
    **kwargs: Unpack[GetFileKwargs],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Fetch data based on a selection criteria for items.

    Args:
        flow_id (str): The ID of the data flow to fetch.
        criteria (MatchCriteria): A sequence of match criteria to filter the data.
        validate (bool, optional): If True, validate the selection against the flow's
            required dimensions. Defaults to False.
        **kwargs: Additional keyword arguments for the fetch_multi function.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: A tuple containing the fetched data and metadata.

    """
    selection = make_wanted(flow_id, criteria)
    return fetch_multi(selection, validate=validate, **kwargs)


# --- quick and dirty testing
if __name__ == "__main__":
    # --- specify a selection from the Wage Price Index (WPI) data flow
    mat_criteria = []
    mat_criteria.append(match_item("Australia", "REGION", MatchType.EXACT))
    mat_criteria.append(
        match_item(
            "Percentage change from corresponding quarter of previous year", "MEASURE", MatchType.EXACT
        )
    )
    mat_criteria.append(match_item("Total hourly rates of pay excluding bonuses", "INDEX", MatchType.PARTIAL))
    mat_criteria.append(match_item("Seas|Trend", "TSEST", MatchType.REGEX))
    mat_criteria.append(match_item("13-Industry aggregate", "INDUSTRY", MatchType.EXACT))
    mat_criteria.append(match_item("Private and Public", "SECTOR", MatchType.EXACT))

    # --- test the selection
    print(make_wanted("WPI", mat_criteria))
    data, meta = fetch_selection("WPI", mat_criteria)
    print(f"Number of data series: {len(meta)}")  # should be 2
    print(meta.T)  # should have the Trend and Seasonally Adjusted series
