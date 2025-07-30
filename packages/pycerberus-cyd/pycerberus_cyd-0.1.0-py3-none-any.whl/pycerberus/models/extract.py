from __future__ import annotations
from typing import Literal

from .common import CerberusBase, Md5, Sha256

from pydantic import BaseModel

class CerberusExtractedNode(BaseModel):
    type: Literal["file", "folder"]
    md5: Md5 | None = None  # Only if file type
    sha256: Sha256 | None = None  # Only if file type
    children: dict[str, CerberusExtractedNode] | None = None


class CerberusExtract(CerberusBase):
    tree: dict[
        str, CerberusExtractedNode
    ]  # This is the children of the analysed file (key: filename or foldername)
    total_extracted_files: int
    version: str  # This is the version of the tool used for this specific extract request
    tool: str
    info: str
