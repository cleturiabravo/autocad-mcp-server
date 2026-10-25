import asyncio

import ezdxf
import pytest

from src import server
from src.models import DrawingError
from src.tools import entity_tools, layer_tools, metadata_tools
from src.tools.dwg_reader import DrawingSession, load_drawing


@pytest.fixture
def dxf_path(tmp_path):
    doc = ezdxf.new("R2018")
    doc.units = 4
    doc.layers.add("WALLS", color=1)
    blk = doc.blocks.new("DOOR")
    blk.add_line((0, 0), (1, 0))
    msp = doc.modelspace()
    msp.add_line((0, 0), (10, 0), dxfattribs={"layer": "WALLS"})
    msp.add_circle((5, 5), 2)
    msp.add_text("Hello", dxfattribs={"layer": "WALLS"})
    msp.add_blockref("DOOR", (3, 3))
    p = tmp_path / "t.dxf"
    doc.saveas(p)
    return str(p)


@pytest.fixture
def doc(dxf_path):
    return load_drawing(dxf_path)


def test_load_errors(tmp_path):
    with pytest.raises(DrawingError):
        load_drawing(str(tmp_path / "missing.dxf"))
    f = tmp_path / "x.txt"
    f.write_text("x")
    with pytest.raises(DrawingError):
        load_drawing(str(f))
    with pytest.raises(DrawingError):
        DrawingSession().require()


def test_layers(doc):
    layers = {l.name: l for l in layer_tools.list_layers(doc)}
    assert layers["WALLS"].entity_count == 2 and layers["WALLS"].color == 1


def test_entities(doc):
    ents = entity_tools.get_entities_by_layer(doc, "WALLS")
    assert {e.type for e in ents} == {"LINE", "TEXT"}
    line = next(e for e in ents if e.type == "LINE")
    assert entity_tools.get_entity_properties(doc, line.handle).geometry["end"] == [10, 0, 0]
    assert len(entity_tools.search_entities(doc, entity_type="circle")) == 1
    assert len(entity_tools.search_entities(doc, text_contains="hel")) == 1
    with pytest.raises(DrawingError):
        entity_tools.get_entities_by_layer(doc, "NOPE")
    with pytest.raises(DrawingError):
        entity_tools.get_entity_properties(doc, "FFFF")


def test_metadata_and_blocks(doc):
    info = metadata_tools.get_drawing_info(doc)
    assert info.entity_count == 4 and info.units == "mm" and info.bounds_max[0] >= 10
    blocks = metadata_tools.list_blocks(doc)
    assert [b.name for b in blocks] == ["DOOR"] and blocks[0].reference_count == 1
    assert metadata_tools.get_block_info(doc, "DOOR").entity_count == 1
    with pytest.raises(DrawingError):
        metadata_tools.get_block_info(doc, "X")


def test_server_tools(dxf_path):
    names = {t.name for t in asyncio.run(server.mcp.list_tools())}
    assert names == {"read_dwg", "list_layers", "get_entities_by_layer",
                     "get_entity_properties", "search_entities",
                     "get_drawing_info", "list_blocks", "get_block_info"}
    assert server.read_dwg(dxf_path)["layer_count"] >= 2
    assert any(l["name"] == "WALLS" for l in server.list_layers())
    with pytest.raises(ValueError):
        server.get_block_info("missing")
