from .common import CerberusBase

class CerberusStrings(CerberusBase):
    strings: dict[str, list[str]] | list[str]
    version: str
