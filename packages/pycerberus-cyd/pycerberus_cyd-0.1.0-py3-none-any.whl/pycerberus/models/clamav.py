from .common import CerberusBase


class CerberusClamav(CerberusBase):
    scan_result: str
    name: str | None = None
    version: str
