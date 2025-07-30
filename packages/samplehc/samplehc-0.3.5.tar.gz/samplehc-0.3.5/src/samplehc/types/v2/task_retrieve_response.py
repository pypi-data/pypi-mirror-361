# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["TaskRetrieveResponse"]


class TaskRetrieveResponse(BaseModel):
    id: str

    status: Literal["running", "waiting-dependencies", "suspended", "completed", "failed", "cancelled"]

    output: Optional[object] = None

    state: Optional[object] = None
