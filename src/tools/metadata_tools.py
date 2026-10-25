"""Drawing metadata and block tools."""
from __future__ import annotations

from collections import Counter

from ezdxf import bbox
from ezdxf.document import Drawing
from ezdxf.units import decode

from ..models import BlockInfo, DrawingError, DrawingInfo


def _count_references(doc: Drawing) -> Counter:
    refs: Counter = Counter()
    layouts = [b for b in doc.blocks]  # includes modelspace
    for layout in layouts:
        for e in layout.query("INSERT"):
            refs[e.dxf.name] += 1
    return refs


def get_drawing_info(doc: Drawing, path: str = "") -> DrawingInfo:
    msp = doc.modelspace()
    types = Counter(e.dxftype() for e in msp)
    extents = bbox.extents(msp)
    header = doc.header
    ltscale = header.get("$LTSCALE")
    return DrawingInfo(
        path=path,
        dxf_version=doc.dxfversion,
        units=decode(header.get("$INSUNITS", 0)),
        measurement="metric" if header.get("$MEASUREMENT", 0) == 1 else "imperial",
        scale=ltscale,
        bounds_min=[round(c, 6) for c in extents.extmin] if extents.has_data else None,
        bounds_max=[round(c, 6) for c in extents.extmax] if extents.has_data else None,
        layer_count=len(doc.layers),
        block_count=len([b for b in doc.blocks if not b.name.startswith("*")]),
        entity_count=sum(types.values()),
        entity_types=dict(types),
    )


def _block_info(doc: Drawing, name: str, refs: Counter) -> BlockInfo:
    block = doc.blocks.get(name)
    return BlockInfo(
        name=block.name,
        base_point=[float(c) for c in block.block.dxf.base_point],
        entity_count=len(block),
        entity_types=dict(Counter(e.dxftype() for e in block)),
        reference_count=refs.get(block.name, 0),
        is_anonymous=block.name.startswith("*"),
    )


def list_blocks(doc: Drawing, include_anonymous: bool = False) -> list[BlockInfo]:
    refs = _count_references(doc)
    return [
        _block_info(doc, b.name, refs)
        for b in doc.blocks
        if include_anonymous or not b.name.startswith("*")
    ]


def get_block_info(doc: Drawing, name: str) -> BlockInfo:
    if name not in doc.blocks:
        raise DrawingError(f"Block not found: {name}")
    return _block_info(doc, name, _count_references(doc))
