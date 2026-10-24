"""Layer query tools."""
from __future__ import annotations

from collections import Counter

from ezdxf.document import Drawing

from ..models import LayerInfo


def list_layers(doc: Drawing) -> list[LayerInfo]:
    counts = Counter(e.dxf.layer for e in doc.modelspace())
    return [
        LayerInfo(
            name=layer.dxf.name,
            color=layer.dxf.color,
            linetype=layer.dxf.linetype,
            lineweight=layer.dxf.lineweight,
            is_on=layer.is_on(),
            is_frozen=layer.is_frozen(),
            is_locked=layer.is_locked(),
            entity_count=counts.get(layer.dxf.name, 0),
        )
        for layer in doc.layers
    ]
