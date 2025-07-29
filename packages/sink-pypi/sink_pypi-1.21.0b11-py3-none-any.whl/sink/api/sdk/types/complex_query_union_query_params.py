# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from typing_extensions import TypedDict

__all__ = ["ComplexQueryUnionQueryParams"]


class ComplexQueryUnionQueryParams(TypedDict, total=False):
    include: Union[str, float, List[str]]
