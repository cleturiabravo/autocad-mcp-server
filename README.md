# autocad-mcp-server

MCP server that lets Claude and other LLMs inspect AutoCAD drawings (DWG/DXF), built on the
[`mcp`](https://pypi.org/project/mcp/) Python SDK and [`ezdxf`](https://ezdxf.mantic.at/). Transport: stdio. Read-only.

## Setup

```bash
pip install -r requirements.txt
python -m pytest            # run tests
python -m src.server        # start server on stdio
```

Python 3.10+. **DXF** files are read natively. **DWG** files are read through ezdxf's
`odafc` add-on, which requires the free
[ODA File Converter](https://www.opendesign.com/guestfiles/oda_file_converter) installed;
otherwise export your drawing to DXF.

## Claude Desktop integration

```json
{
  "mcpServers": {
    "autocad": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/autocad-mcp-server"
    }
  }
}
```

See `example_usage.py` for a programmatic client.

## API reference

Call `read_dwg` first; other tools operate on the loaded drawing. Errors (missing file,
unknown layer/block/handle, no drawing loaded) are returned as tool errors.

| Tool | Arguments | Description |
|---|---|---|
| `read_dwg` | `path` | Load a DWG/DXF; returns drawing summary |
| `list_layers` | – | Layers with color, linetype, lineweight, on/frozen/locked, entity count |
| `get_entities_by_layer` | `layer`, `limit=100` | Modelspace entities on a layer |
| `get_entity_properties` | `handle` | Layer, color, linetype, lineweight and geometry of one entity |
| `search_entities` | `entity_type?`, `layer?`, `color?`, `linetype?`, `text_contains?`, `limit=100` | Filter entities |
| `get_drawing_info` | – | Version, units, scale (`$LTSCALE`), bounds, counts, entity types |
| `list_blocks` | `include_anonymous=false` | Block definitions with reference counts |
| `get_block_info` | `name` | Base point, contents and reference count of a block |

Example: ask Claude *"Load plan.dxf and tell me which layers contain TEXT entities"* — it will call
`read_dwg`, `list_layers`, then `search_entities(entity_type="TEXT")`.
