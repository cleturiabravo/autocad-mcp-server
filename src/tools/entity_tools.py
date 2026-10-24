"""Entity query and analysis tools."""
from __future__ import annotations

from typing import Any, Optional

from ezdxf.document import Drawing
from ezdxf.entities import DXFEntity

from ..models import DrawingError, EntityInfo


def _pt(v: Any) -> list[float]:
    return [round(float(c), 6) for c in v]


def _geometry(e: DXFEntity) -> dict[str, Any]:
    t = e.dxftype()
    d = e.dxf
    g: dict[str, Any] = {}
    if t == "LINE":
        g = {"start": _pt(d.start), "end": _pt(d.end)}
    elif t == "CIRCLE":
        g = {"center": _pt(d.center), "radius": d.radius}
    elif t == "ARC":
        g = {"center": _pt(d.center), "radius": d.radius,
             "start_angle": d.start_angle, "end_angle": d.end_angle}
    elif t in ("TEXT", "MTEXT"):
        g = {"text": e.dxf.text if t == "TEXT" else e.text,
             "insert": _pt(d.insert)}
    elif t == "LWPOLYLINE":
        g = {"points": [[round(x, 6), round(y, 6)] for x, y, *_ in e.get_points()],
             "closed": bool(e.closed)}
    elif t == "INSERT":
        g = {"block": d.name, "insert": _pt(d.insert),
             "rotation": d.get("rotation", 0.0)}
    elif t == "POINT":
        g = {"location": _pt(d.location)}
    return g


def entity_info(e: DXFEntity) -> EntityInfo:
    d = e.dxf
    return EntityInfo(
        handle=d.handle,
        type=e.dxftype(),
        layer=d.get("layer", "0"),
        color=d.get("color", 256),
        linetype=d.get("linetype", "BYLAYER"),
        lineweight=d.get("lineweight", -1),
        geometry=_geometry(e),
    )


def _limit(items: list[Any], limit: int) -> list[Any]:
    return items[: max(limit, 0)]


def get_entities_by_layer(doc: Drawing, layer: str, limit: int = 100) -> list[EntityInfo]:
    if layer not in doc.layers:
        raise DrawingError(f"Layer not found: {layer}")
    ents = [e for e in doc.modelspace() if e.dxf.layer == layer]
    return [entity_info(e) for e in _limit(ents, limit)]


def get_entity_properties(doc: Drawing, handle: str) -> EntityInfo:
    e = doc.entitydb.get(handle.upper())
    if e is None:
        raise DrawingError(f"Entity not found: {handle}")
    return entity_info(e)


def search_entities(
    doc: Drawing,
    entity_type: Optional[str] = None,
    layer: Optional[str] = None,
    color: Optional[int] = None,
    linetype: Optional[str] = None,
    text_contains: Optional[str] = None,
    limit: int = 100,
) -> list[EntityInfo]:
    results: list[EntityInfo] = []
    for e in doc.modelspace():
        if entity_type and e.dxftype().upper() != entity_type.upper():
            continue
        if layer and e.dxf.get("layer", "0") != layer:
            continue
        if color is not None and e.dxf.get("color", 256) != color:
            continue
        if linetype and e.dxf.get("linetype", "BYLAYER").upper() != linetype.upper():
            continue
        info = entity_info(e)
        if text_contains:
            txt = str(info.geometry.get("text", ""))
            if text_contains.lower() not in txt.lower():
                continue
        results.append(info)
        if len(results) >= limit:
            break
    return results
