import re

from copy import deepcopy
from rapidfuzz import fuzz
from typing import Literal


def match_val(
    val: str,
    vals: list[str],
    ignore_case: bool = True,
    spaces_to: Literal["keep", "ignore" "merge"] = "merge",
    use_fuzz: bool = False,
) -> tuple[str, int, float]:
    """
    Return:
        - closest val
        - index of the closest val in the list
        - similarity score (0-1)

    score = (1 – d/L)
    * d: distance by insert(1)/delete(1)/replace(2)
    * L: length sum of both strings
    """
    if not vals:
        return None, None, 0

    xval = deepcopy(val)
    xvals = deepcopy(vals)

    if spaces_to == "ignore":
        xval = re.sub(r"\s+", "", val.strip())
        xvals = [re.sub(r"\s+", "", v.strip()) for v in vals]
    elif spaces_to == "merge":
        xval = re.sub(r"\s+", " ", val.strip())
        xvals = [re.sub(r"\s+", " ", v.strip()) for v in vals]
    else:
        pass

    if ignore_case:
        xval = xval.lower()
        xvals = [v.lower() for v in xvals]

    if use_fuzz:
        scores = [fuzz.ratio(val, v) / 100.0 for v in xvals]
    else:
        scores = [1 if val == v else 0 for v in xvals]

    midx, max_score = None, 0.0
    for i, s in enumerate(scores):
        if s > max_score:
            midx = i
            max_score = s
    if midx is None:
        mval = None
    else:
        mval = vals[midx]
    return mval, midx, max_score
