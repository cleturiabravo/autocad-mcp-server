"""Data models and type definitions."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Optional


class DrawingError(Exception):
    """Raised for user-facing errors (bad path, no drawing loaded, unknown name...)."""


@dataclass
class LayerInfo:
    name: str
    color: int
    linetype: str
    lineweight: int
    is_on: bool
    is_frozen: bool
    is_locked: bool
    entity_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EntityInfo:
    handle: str
    type: str
    layer: str
    color: int
    linetype: str
    lineweight: int
    geometry: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BlockInfo:
    name: str
    base_point: list[float]
    entity_count: int
    entity_types: dict[str, int]
    reference_count: int
    is_anonymous: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DrawingInfo:
    path: str
    dxf_version: str
    units: str
    measurement: str
    scale: Optional[float]
    bounds_min: Optional[list[float]]
    bounds_max: Optional[list[float]]
    layer_count: int
    block_count: int
    entity_count: int
    entity_types: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
