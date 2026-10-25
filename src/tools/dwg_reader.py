"""DWG/DXF file loading. DXF is read natively with ezdxf; DWG requires the
ODA File Converter (used through ezdxf.addons.odafc)."""
from __future__ import annotations

import logging
import os
from typing import Optional

import ezdxf
from ezdxf.document import Drawing

from ..models import DrawingError

logger = logging.getLogger(__name__)


def load_drawing(path: str) -> Drawing:
    if not path or not os.path.isfile(path):
        raise DrawingError(f"File not found: {path}")
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".dxf":
            return ezdxf.readfile(path)
        if ext == ".dwg":
            from ezdxf.addons import odafc

            if not odafc.is_installed():
                raise DrawingError(
                    "Reading DWG files requires the ODA File Converter "
                    "(https://www.opendesign.com/guestfiles/oda_file_converter). "
                    "Install it, or export the drawing to DXF."
                )
            return odafc.readfile(path)
    except DrawingError:
        raise
    except Exception as exc:  # ezdxf raises several error types
        raise DrawingError(f"Could not read {path}: {exc}") from exc
    raise DrawingError(f"Unsupported file type '{ext}'. Use .dwg or .dxf")


class DrawingSession:
    """Holds the currently loaded drawing."""

    def __init__(self) -> None:
        self.doc: Optional[Drawing] = None
        self.path: Optional[str] = None

    def load(self, path: str) -> Drawing:
        self.doc = load_drawing(path)
        self.path = os.path.abspath(path)
        logger.info("Loaded %s", self.path)
        return self.doc

    def require(self) -> Drawing:
        if self.doc is None:
            raise DrawingError("No drawing loaded. Call read_dwg first.")
        return self.doc
