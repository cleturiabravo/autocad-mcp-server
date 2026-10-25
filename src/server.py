"""AutoCAD MCP server (stdio transport). Run with: python -m src.server"""
from __future__ import annotations

import logging
import sys
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from .models import DrawingError
from .tools import entity_tools, layer_tools, metadata_tools
from .tools.dwg_reader import DrawingSession

# stdout is reserved for the MCP protocol; log to stderr.
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("autocad-mcp")

mcp = FastMCP("autocad-mcp-server")
session = DrawingSession()


def _guard(fn):
    """Convert DrawingError to a clear error message and log unexpected errors."""
    import functools

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except DrawingError as exc:
            raise ValueError(str(exc)) from exc
        except Exception:
            logger.exception("Tool %s failed", fn.__name__)
            raise

    return wrapper


@mcp.tool()
@_guard
def read_dwg(path: str) -> dict[str, Any]:
    """Load a DWG or DXF file and return a summary. DWG needs the ODA File Converter."""
    doc = session.load(path)
    return metadata_tools.get_drawing_info(doc, session.path or path).to_dict()


@mcp.tool()
@_guard
def list_layers() -> list[dict[str, Any]]:
    """List all layers with color, linetype, lineweight, state and entity count."""
    return [l.to_dict() for l in layer_tools.list_layers(session.require())]


@mcp.tool()
@_guard
def get_entities_by_layer(layer: str, limit: int = 100) -> list[dict[str, Any]]:
    """Get modelspace entities on a layer (up to `limit`)."""
    return [e.to_dict() for e in
            entity_tools.get_entities_by_layer(session.require(), layer, limit)]


@mcp.tool()
@_guard
def get_entity_properties(handle: str) -> dict[str, Any]:
    """Get color, linetype, lineweight, layer and geometry of an entity by handle."""
    return entity_tools.get_entity_properties(session.require(), handle).to_dict()


@mcp.tool()
@_guard
def search_entities(
    entity_type: Optional[str] = None,
    layer: Optional[str] = None,
    color: Optional[int] = None,
    linetype: Optional[str] = None,
    text_contains: Optional[str] = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """Search modelspace entities by type, layer, color, linetype or text content."""
    return [e.to_dict() for e in entity_tools.search_entities(
        session.require(), entity_type, layer, color, linetype, text_contains, limit)]


@mcp.tool()
@_guard
def get_drawing_info() -> dict[str, Any]:
    """Get drawing metadata: version, units, scale, bounds, and counts."""
    return metadata_tools.get_drawing_info(session.require(), session.path or "").to_dict()


@mcp.tool()
@_guard
def list_blocks(include_anonymous: bool = False) -> list[dict[str, Any]]:
    """List block definitions with reference counts."""
    return [b.to_dict() for b in
            metadata_tools.list_blocks(session.require(), include_anonymous)]


@mcp.tool()
@_guard
def get_block_info(name: str) -> dict[str, Any]:
    """Get properties of a block definition."""
    return metadata_tools.get_block_info(session.require(), name).to_dict()


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
