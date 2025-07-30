from .common import CerberusBase
from pydantic import BaseModel

class CerberusDieScanDetect(BaseModel):
    filetype: str
    parentfilepart: str
    info: str
    name: str
    string: str
    type: str
    version: str


class CerberusDieEntropyRecord(BaseModel):
    entropy: float
    name: str
    offset: int
    size: int
    status: str


class CerberusDieFileInfo(BaseModel):
    architecture: str | None = None
    endianness: str | None = None
    mode: str | None = None
    os: str | None = None
    type: str | None = None


class CerberusDie(CerberusBase):
    scan: list[CerberusDieScanDetect]
    entropy: list[CerberusDieEntropyRecord]
    file_info: CerberusDieFileInfo
    version: str
