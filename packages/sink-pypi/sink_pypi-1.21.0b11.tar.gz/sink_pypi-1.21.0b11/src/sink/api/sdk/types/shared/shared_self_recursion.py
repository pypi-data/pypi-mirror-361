# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

from ..._compat import PYDANTIC_V2
from ..._models import BaseModel

__all__ = ["SharedSelfRecursion"]


class SharedSelfRecursion(BaseModel):
    name: str

    child: Optional["SharedSelfRecursion"] = None


if PYDANTIC_V2:
    SharedSelfRecursion.model_rebuild()
else:
    SharedSelfRecursion.update_forward_refs()  # type: ignore
