from .common import CerberusBase


class CerberusFilter(CerberusBase):
    status: str
    md5: str | None = None
    sha256: str | None = None
    category: str | None = None
    filenames: list[str] | None = None
    malware_name: str | None = None
    malware_types: dict[str, int] | None = None
    packer_name: str | None = None
    version: str

