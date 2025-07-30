"""Data classes for :mod:`auraxium.ps2._objective`."""

from typing import Optional

from .base import RESTPayload

__all__ = [
    'ObjectiveData',
    'ObjectiveTypeData'
]


class ObjectiveData(RESTPayload):
    """Data class for :class:`auraxium.ps2.Objective`.

    This class mirrors the payload data returned by the API, you may
    use its attributes as keys in filters or queries.
    """

    objective_id: int
    objective_type_id: int
    objective_group_id: int
    param1: Optional[str] = None
    param2: Optional[str] = None
    param3: Optional[str] = None
    param4: Optional[str] = None
    param5: Optional[str] = None
    param6: Optional[str] = None
    param7: Optional[str] = None
    param8: Optional[str] = None
    param9: Optional[str] = None


class ObjectiveTypeData(RESTPayload):
    """Data class for :class:`auraxium.ps2.ObjectiveType`.

    This class mirrors the payload data returned by the API, you may
    use its attributes as keys in filters or queries.
    """

    objective_type_id: int
    description: str
    param1: Optional[str] = None
    param2: Optional[str] = None
    param3: Optional[str] = None
    param4: Optional[str] = None
    param5: Optional[str] = None
    param6: Optional[str] = None
    param7: Optional[str] = None
    param8: Optional[str] = None
    param9: Optional[str] = None
